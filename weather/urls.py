from django.urls import path
from .import views
from .views import index


urlpatterns = [
    path('', views.index, name='index'),
    path('autocomplete/', views.autocomplete, name='autocomplete'),
    path('api/status', views.weather_status, name='weather_status'),
    path('your-weather-endpoint/', index, name='index'),

]