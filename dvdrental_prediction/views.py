from django.shortcuts import render
from .models import Movie, FilmCategory
from .forms import MovieSearchForm
from .models import ModelInfo
import os
from django.conf import settings
import json
import joblib
import numpy as np
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import CustomerPredictionForm


def home(request):
    return render(request, 'dvdrental_prediction/home.html')

def about(request):
    return render(request, 'dvdrental_prediction/about.html')

def movie_list(request):
    movies = Movie.objects.select_related('language').all()
    form = MovieSearchForm()
    return render(request, 'dvdrental_prediction/movie_list.html', {'movies': movies, 'form': form})

def movie_detail(request, film_id):
    movie = Movie.objects.get(film_id=film_id)
    actors = movie.actors.all()
    return render(request, 'dvdrental_prediction/movie_detail.html', {'movie': movie, 'actors': actors})

def search_result(request):
    form = MovieSearchForm(request.GET)
    movies = Movie.objects.select_related('language').all()

    if form.is_valid():
        actor = form.cleaned_data.get('actor')
        category = form.cleaned_data.get('category')
        language = form.cleaned_data.get('language')

        if actor:
            movies = movies.filter(actors=actor)
        if category:
            movies = movies.filter(filmcategory__category=category)
        if language:
            movies = movies.filter(language=language)
    return render(request, 'dvdrental_prediction/movie_search.html', {'form': form, 'movies': movies})

def model_info(request):
    models = ModelInfo.objects.all()
    return render(request, 'dvdrental_prediction/model_info.html', {'models': models})

def customer_prediction_view(request):
    form = CustomerPredictionForm()
    return render(request, 'dvdrental_prediction/dashboard.html', {'form': form})


# ================== FIX DI SINI ==================

model_path = os.path.join(settings.BASE_DIR, 'final_customer_model.pkl')
model = joblib.load(model_path)

@csrf_exempt
def predict_customer(request):
    print(f"Request method: {request.method}")
    if request.method == 'POST':
        data = json.loads(request.body)
        print(f"Data received: {data}")

        features = np.array([
            data["store_id"],
            data["active"],
            data["total_payment"],
            data["payment_count"],
            data["average_payment"],
        ]).reshape(1, -1)

        prediction = model.predict(features)[0]
        probability = model.predict_proba(features)[0].tolist()

        return JsonResponse({
            "prediction": int(prediction),
            "probability": probability
        })