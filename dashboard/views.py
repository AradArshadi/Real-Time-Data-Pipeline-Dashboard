from django.shortcuts import render
from pipeline.models import WeatherRecord

def dashboard_view(request):
    cities = ['London', 'Berlin', 'Istanbul', 'Tehran', 'Toronto']
    data = {}
    for city in cities:
        latest = WeatherRecord.objects.filter(city=city).first()
        data[city] = latest
    return render(request, 'dashboard/index.html', {'data': data})