import requests
from django.conf import settings
from .models import WeatherRecord

def fetch_weather(city):
    url = 'https://api.openweathermap.org/data/2.5/weather'
    params = {
        'q': city,
        'appid': settings.WEATHER_API_KEY,
        'units': 'metric'
    }
    response = requests.get(url, params=params)
    data = response.json()

    return WeatherRecord.objects.create(
        city=city,
        temperature=data['main']['temp'],
        humidity=data['main']['humidity'],
        description=data['weather'][0]['description'],
        wind_speed=data['wind']['speed'],
        pressure=data['main']['pressure'],
    )

def fetch_all_cities():
    results = []
    for city in settings.CITIES:
        record = fetch_weather(city)
        results.append(record)
    return results