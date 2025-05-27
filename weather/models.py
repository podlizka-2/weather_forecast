from django.db import models

class CitySearch(models.Model):
    name = models.CharField(max_length=200, unique=True)
    count = models.PositiveIntegerField(default=0)

class SearchHistory(models.Model):
    session_key = models.CharField(max_length=40)
    city = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
