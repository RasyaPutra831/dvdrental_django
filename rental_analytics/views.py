from django.shortcuts import render
from .forms import MovieForm
import json
import joblib
import numpy as np
from .models import ModelInfo, PredictionHistory
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from collections import Counter



# HOME
def home(request):
    filter_by = request.GET.get('filter_by')
    value = request.GET.get('value')
    sort = request.GET.get('sort')
    page = int(request.GET.get('page', 1))

    if filter_by == "None":
        filter_by = None
    if value == "None":
        value = None
    if sort == "None":
        sort = None

    limit = 10
    offset = (page - 1) * limit

    where_clause = ""
    params = []

    if filter_by and value:
        where_clause = f"WHERE {filter_by} = %s"
        params.append(value)

    order_clause = ""
    if sort == "high":
        order_clause = "ORDER BY total_revenue DESC"
    elif sort == "low":
        order_clause = "ORDER BY total_revenue ASC"

    query = f"""
        SELECT *
        FROM movie_analytics
        {where_clause}
        {order_clause}
        LIMIT %s OFFSET %s
    """

    count_query = f"""
        SELECT COUNT(*)
        FROM movie_analytics
        {where_clause}
    """

    with connection.cursor() as cursor:
        cursor.execute(query, params + [limit, offset])
        columns = [col[0] for col in cursor.description]
        movies = [dict(zip(columns, row)) for row in cursor.fetchall()]

        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]

    total_pages = max(1, (total // limit) + (1 if total % limit else 0))

    current_page = page
    window = 2

    start_page = max(1, current_page - window)
    end_page = min(total_pages, current_page + window)

    page_range = list(range(start_page, end_page + 1))

    show_first = start_page > 1
    show_last = end_page < total_pages

    filter_values = []
    if filter_by:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT DISTINCT {filter_by} FROM movie_analytics")
            filter_values = [row[0] for row in cursor.fetchall()]

    # DASHBOARD DATA
    popular_qs = PredictionHistory.objects.filter(
        prediction_type='movie',
        prediction='Popular'
    )

    not_popular_qs = PredictionHistory.objects.filter(
        prediction_type='movie',
        prediction='Not Popular'
    )

    popular_titles = [x['title'] for x in [m.input_data for m in popular_qs] if x.get('title')]
    not_popular_titles = [x['title'] for x in [m.input_data for m in not_popular_qs] if x.get('title')]

    # TOP GENRE POPULAR
    genre_list = [
        m.input_data.get('category')
        for m in popular_qs
        if m.input_data.get('category')
    ]

    genre_counter = Counter(genre_list)

    genre_labels = list(genre_counter.keys())
    genre_values = list(genre_counter.values())

    return render(request, 'rental_analytics/home.html', {
        'movies': movies,
        'page': page,
        'total_pages': total_pages,
        'page_range': page_range,
        'show_first': show_first,
        'show_last': show_last,
        'filter_values': filter_values,
        'selected_filter': filter_by,
        'selected_value': value,
        'selected_sort': sort,


        'popular_titles': popular_titles,
        'not_popular_titles': not_popular_titles,
        'popular_count': len(popular_titles),
        'not_popular_count': len(not_popular_titles),
        'genre_labels': genre_labels,
        'genre_values': genre_values,
    })


# MOVIE PAGE + FILTER HISTORY
def movie_page(request):
    result_filter = request.GET.get('result')

    qs = PredictionHistory.objects.filter(prediction_type='movie')

    if result_filter:
        qs = qs.filter(prediction=result_filter)

    movies = qs.order_by('-created_at')

    return render(request, 'rental_analytics/movie.html', {
        'movies': movies
    })


@csrf_exempt
def get_movie_history(request):
    result_filter = request.GET.get('result', '')
    qs = PredictionHistory.objects.filter(prediction_type='movie').order_by('-created_at')

    if result_filter:
        qs = qs.filter(prediction=result_filter)

    history = list(qs.values('id', 'input_data', 'prediction', 'confidence', 'created_at'))

    return JsonResponse(history, safe=False)


# AUTOCOMPLETE
def search_movie(request):
    q = request.GET.get('q', '')

    if not q:
        return JsonResponse([], safe=False)

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT title
            FROM movie_analytics
            WHERE LOWER(title) LIKE LOWER(%s)
            ORDER BY title ASC
            LIMIT 10
        """, [f"{q}%"])

        data = [row[0] for row in cursor.fetchall()]

    return JsonResponse(data, safe=False)


def get_movie_detail(request):
    title = request.GET.get('title')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                ma.category, 
                ma.total_revenue, 
                COALESCE(f.length, 0) as film_length,
                ma.rating
            FROM movie_analytics ma
            LEFT JOIN film f ON ma.film_id = f.film_id
            WHERE ma.title = %s
            LIMIT 1
        """, [title])

        row = cursor.fetchone()

    if not row:
        return JsonResponse({'error': 'not found'})

    category, revenue, length, rating = row

    return JsonResponse({
        'category': category,
        'total_revenue': float(revenue),
        'film_length': int(length) if length else 0,
        'rating': rating
    })


# PREDICT
@csrf_exempt
def predict_movie(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        model_info = ModelInfo.objects.order_by('-created_at').first()
        model = joblib.load(model_info.file_path)

        rating_map = {'G':0,'PG':1,'PG-13':2,'R':3,'NC-17':4}
        category_map = {
            'Action':0,'Animation':1,'Children':2,'Classics':3,
            'Comedy':4,'Documentary':5,'Drama':6,'Family':7,
            'Foreign':8,'Games':9,'Horror':10,'Music':11,
            'New':12,'Sci-Fi':13,'Sports':14,'Travel':15
        }

        features = np.array([[
            category_map.get(data['category'],0),
            float(data['total_revenue']),
            int(data['film_length']),
            rating_map.get(data['rating'],0),
            int(data['predict_month'])
        ]])

        pred = model.predict(features)[0]
        prob = model.predict_proba(features)[0]
        confidence = float(max(prob))

        label = "Popular" if pred == 1 else "Not Popular"

        data['title'] = data.get('title', 'Unknown')

        return JsonResponse({
            'prediction': int(pred),
            'confidence': confidence,
            'label': label,
            'input_data': data
        })


# MANUAL SAVE
@csrf_exempt
def save_movie_prediction(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        PredictionHistory.objects.create(
            prediction_type='movie',
            input_data=data['input_data'],
            prediction=data['label'],
            confidence=data['confidence'],
            model_used="Random Forest"
        )

        return JsonResponse({'status': 'saved'})


# DELETE SELECTED
@csrf_exempt
def delete_selected_movies(request):
    data = json.loads(request.body)
    ids = data.get('ids', [])
    PredictionHistory.objects.filter(id__in=ids).delete()
    return JsonResponse({'status': 'deleted'})


# CLEAR ALL
@csrf_exempt
def clear_all_movies(request):
    PredictionHistory.objects.filter(prediction_type='movie').delete()
    return JsonResponse({'status': 'cleared'})