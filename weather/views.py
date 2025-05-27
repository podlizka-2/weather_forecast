from django.shortcuts import render
from django.hhtp import JsonResponse
import requests
from models import CitySearch, SearchHistory
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ObjectDoesNotExist





# Create your views here.
