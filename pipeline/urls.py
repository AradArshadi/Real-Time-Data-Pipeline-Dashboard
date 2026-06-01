from django.urls import path
from .views import WeatherListView

urlpatterns = [
    path('weather/', WeatherListView.as_view(), name='weather-list'),
]