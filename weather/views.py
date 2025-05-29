from django.shortcuts import render
from django.http import JsonResponse 
import requests
from .models import CitySearch
import os
from django.conf import settings

OPENCAGE_API_KEY = settings.OPENCAGE_API_KEY

def index(request):
    context = {
        'weather': None,
        'city': '',
        'history': request.session.get('search_history', []),
        'error': None,
        'suggest_city': None
    }

    # Предлагаем последний просмотренный город.
    if not request.method == 'POST' and context['history']:
        context['suggest_city'] = context['history'][0]

    if request.method == 'POST':
        city_name = request.POST.get('city')
        if not city_name:
            context['error'] = 'Введите название города'
            return render(request, 'weather/index.html', context)

        # Получение координат.
        geo_url = f"https://api.opencagedata.com/geocode/v1/json?q={city_name}&key={OPENCAGE_API_KEY}&limit=1"
        try:
            geo_response = requests.get(geo_url)
            geo_data = geo_response.json()
        except Exception as e:
            context['error'] = f'Ошибка геокодера: {str(e)}'
            return render(request, 'weather/index.html', context)

        if geo_response.status_code == 200 and geo_data.get('results'):
            result = geo_data['results'][0]
            lat = result['geometry']['lat']
            lng = result['geometry']['lng']
            
            # Запрос погоды.
            weather_url = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={lat}&longitude={lng}"
                f"&current_weather=true"
                f"&timezone=auto"
            )
            
            try:
                weather_response = requests.get(weather_url)
                weather_data = weather_response.json()
            except Exception as e:
                context['error'] = f'Ошибка погодного сервиса: {str(e)}'
                return render(request, 'weather/index.html', context)

            if weather_response.status_code == 200 and 'current_weather' in weather_data:
                # Сохранение города.
                city_obj, created = CitySearch.objects.get_or_create(name=city_name)
                city_obj.count += 1
                city_obj.save()
                
                # Обновление истории.
                history = request.session.get('search_history', [])
                if city_name not in history:
                    history.insert(0, city_name)
                    history = history[:5]  # Сохраняем только 5 последних.
                    request.session['search_history'] = history
                    context['history'] = history

                context.update({
                    'weather': weather_data['current_weather'],
                    'city': city_name
                })
            else:
                context['error'] = 'Данные о погоде недоступны'
        else:
            context['error'] = 'Город не найден'

    return render(request, 'weather/index.html', context)

    
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