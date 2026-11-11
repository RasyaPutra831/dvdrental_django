from django.urls import path
from . import views
from . import admin_view
from .views import customer_prediction_view, predict_customer

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('movies/', views.movie_list, name='movie_list'),
    path('movies/<int:film_id>/', views.movie_detail, name='movie_detail'),
    path('search/', views.search_result, name='search_result'),
    path('admin/retrain-model/<int:model_id>/', admin_view.retrain_model_view, name='retrain_model'),
    path('predict-view/', customer_prediction_view, name='customer_prediction_view'),
    path('predict-customer/', predict_customer, name='predict_customer'),
    path('', views.customer_prediction_view, name='dashboard'),
]