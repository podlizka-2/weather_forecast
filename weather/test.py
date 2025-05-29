from django.test import TestCase, Client
from django.urls import reverse
from .models import CitySearch
import json
from unittest.mock import patch

class WeatherAppTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.index_url = reverse('index')
        self.autocomplete_url = reverse('autocomplete')
        self.status_url = reverse('weather_status')
        
        # Создаем тестовые данные
        CitySearch.objects.create(name="Москва", count=5)
        CitySearch.objects.create(name="Санкт-Петербург", count=3)

    def test_index_get(self):
        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'weather/index.html')
        self.assertContains(response, 'Прогноз погоды')

    @patch('weather.views.requests.get')
    def test_index_post_valid_city(self, mock_get):
        # Мокаем API запросы
        geo_mock = type('MockResponse', (), {
            'status_code': 200,
            'json': lambda: {
                'results': [{
                    'geometry': {'lat': 55.7558, 'lng': 37.6176},
                    'formatted': 'Москва, Россия'
                }]
            }
        })
        
        weather_mock = type('MockResponse', (), {
            'status_code': 200,
            'json': lambda: {
                'current_weather': {
                    'temperature': 20.5,
                    'windspeed': 15.3,
                    'winddirection': 180,
                    'time': '2023-05-29T12:00'
                }
            }
        })
        
        mock_get.side_effect = [geo_mock, weather_mock]
        
        response = self.client.post(self.index_url, {'city': 'Москва'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Погода в Москва')
        self.assertContains(response, '20.5')
        
        # Проверяем, что счетчик увеличился
        moscow = CitySearch.objects.get(name="Москва")
        self.assertEqual(moscow.count, 6)

    def test_index_post_invalid_city(self):
        response = self.client.post(self.index_url, {'city': 'НесуществующийГород'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Город не найден')

    def test_autocomplete(self):
        response = self.client.get(self.autocomplete_url, {'term': 'мос'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertGreater(len(data), 0)
        self.assertIn('Москва', data)

    def test_weather_status(self):
        response = self.client.get(self.status_url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['name'], 'Москва')
        self.assertEqual(data[0]['count'], 5)

    def test_session_history(self):
        # Первый запрос
        session = self.client.session
        session['search_history'] = ['Санкт-Петербург']
        session.save()
        
        response = self.client.get(self.index_url)
        self.assertContains(response, 'Санкт-Петербург')
        
        # Добавляем новый город
        with patch('weather.views.requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {
                'results': [{'geometry': {'lat': 55.7558, 'lng': 37.6176}}],
                'current_weather': {'temperature': 20}
            }
            
            response = self.client.post(self.index_url, {'city': 'Казань'})
            self.assertEqual(response.status_code, 200)
            
            # Проверяем обновление истории
            session = self.client.session
            self.assertEqual(session['search_history'], ['Казань', 'Санкт-Петербург'])
