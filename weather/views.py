from django.shortcuts import render
from django.http import JsonResponse 
import requests
from .models import CitySearch
import os

# Получите ваш API-ключ OpenCage Geocoder и установите как переменную окружения
OPENCAGE_API_KEY = os.getenv('OPENCAGE_API_KEY')

def index(request):
    # Обработка формы.
    if request.method == 'POST':
        city_name = request.POST.get('city')
        # Получение координат через OpenCage Geocoder.
        geo_url = f"https://api.opencagedata.com/geocode/v1/json?q={city_name}&key={OPENCAGE_API_KEY}&limit=1"
        response = requests.get(geo_url)
        if response.status_code == 200:
            data = response.json()
            if data['results']:
                result = data['results'][0]
                lat = result['geometry']['lat']
                lng = result['geometry']['lng']
                # Запрос погоды.
                weather_url = f"https://open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&current_weather=true"
                weather_response = requests.get(weather_url)
                if weather_response.status_code == 200:
                    weather_data = weather_response.json()
                    current_weather = weather_data.get('current_weather', {})
                    # Сохранение города.
                    city, created = CitySearch.objects.get_or_create(name=city_name)
                    city.count += 1
                    city.save()
                    # Обработка истории поиска в сессии.
                    history = request.session.get('search_history', [])
                    if city_name not in history:
                        history.insert(0, city_name)
                        if len(history) > 5:
                            history.pop()
                        request.session['search_history'] = history
                    
                    return render(request, 'weather/index.html', {
                        'weather': current_weather,
                        'city': city_name,
                        'history': history
                    })
            else:
                # Не найден город или пустой результат.
                return render(request, 'weather/index.html', {
                    'error': 'Город не найден/выберите другой.'
                })
        else:
            return render(request, 'weather/index.html', {
                'error': 'Ошибка при обращении к геокодеру.'
            })

    # GET-запрос (отображение страницы).
    history = request.session.get('search_history', [])
    return render(request, 'weather/index.html', {'history': history})

def autocomplete(request):
    term = request.GET.get('term', '')
    suggestions = []
    if term:
        # Используем OpenCage Geocoder для автодополнения.
        geo_url = f"https://api.opencagedata.com/geocode/v1/json?q={term}&key={OPENCAGE_API_KEY}&limit=5"
        response = requests.get(geo_url)
        if response.status_code == 200:
            data = response.json()
            if data['results']:
                for place in data['results']:
                    suggestions.append(place['formatted'])
    return JsonResponse(suggestions, safe=False)

def weather_status(request):
    status = CitySearch.objects.all().values('name', 'count')
    return JsonResponse(list(status), safe=False)