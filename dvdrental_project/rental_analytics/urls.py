from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('movie/', views.movie_page, name='movie_page'),
    path('predict-movie/', views.predict_movie, name='predict_movie'),

    path('search-movie/', views.search_movie),
    path('get-movie-detail/', views.get_movie_detail),

    path('save-movie/', views.save_movie_prediction),
    path('get-history/', views.get_movie_history),
    path('delete-movie-selected/', views.delete_selected_movies),
    path('clear-movies/', views.clear_all_movies),
]
