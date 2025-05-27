from django.urls import path
from .import views

urlpatterns = [
    path('', views.index, name='index'),
    path('autocomplete/', views.autocomplete, name='autocomplete'),
    path('api/status', views.weather_status, name='weather_status'),
]