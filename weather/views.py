
from django.shortcuts import render
from django.http import JsonResponse 
import requests
from models import CitySearch
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ObjectDoesNotExist

def index(request):
    #Обработка формы.
    if request.method =='POST':
        city_name = request.POST.get('city')
        #Получение координат.
        geo_url = f"https://nominatim.opensreetmap.org/search?format=json&q={city_name}"
        response = requests.get(geo_url)
        if response.status_code == 200 and response.json():
            data = response.json()[0]
            lat = data['lat']
            long = data['long']
            #Запрос погоды.
            weather_url = f"https://open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&current_weather=true"
            weather_response = requests.get(weather_url)
            if weather_response.status_code == 200:
                weather_data = weather_response.json()
                current_weather = weather_data.get('current_weather', {})
                #Сохранение города.
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
        #Если не найден город-ошибка.
        return render(request, 'weather/index.html', {
            'error':'Город не найден/выберите другой.' 
        })
    #GET-запрос(отображение страницы).
    history = request.session.get('search_history', [])
    return render(request, 'weather/index.html', {'history':history})
def autocomplete(request):
    term = request.GET.get('term', '')
    suggestions = []
    if term:
        geo_url = f"https://nominatim.opensreetmap.org/search?format=json&q={term}"
        response = requests.get(geo_url)
        if response.status_code == 200:
            for place in response.json():
                suggestions.append(place['display_name'])
    return JsonResponse(suggestions, safe=False)


def weather_status(request):
    status = CitySearch.objects.all().values('name', 'count')
    return JsonResponse(list(status), safe=False)
