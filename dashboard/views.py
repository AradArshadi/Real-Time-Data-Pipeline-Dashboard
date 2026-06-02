import csv
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.dateparse import parse_date

from pipeline.models import WeatherRecord


def dashboard_home(request):
    weather_data = WeatherRecord.objects.all()

    start_date = request.GET.get("start_date", "")
    end_date = request.GET.get("end_date", "")

    start = parse_date(start_date) if start_date else None
    end = parse_date(end_date) if end_date else None

    if start:
        weather_data = weather_data.filter(recorded_at__date__gte=start)

    if end:
        weather_data = weather_data.filter(recorded_at__date__lte=end)

    # Latest record per city
    latest_weather = weather_data.order_by("city", "-recorded_at").distinct("city")

    chart_labels = [item.city for item in latest_weather]
    chart_temperatures = [item.temperature for item in latest_weather]

    context = {
        "weather_data": latest_weather,
        "start_date": start_date,
        "end_date": end_date,
        "chart_labels": chart_labels,
        "chart_temperatures": chart_temperatures,
    }

    return render(request, "dashboard/home.html", context)


def export_weather_csv(request):
    weather_data = WeatherRecord.objects.all()

    start_date = request.GET.get("start_date", "")
    end_date = request.GET.get("end_date", "")

    start = parse_date(start_date) if start_date else None
    end = parse_date(end_date) if end_date else None

    if start:
        weather_data = weather_data.filter(recorded_at__date__gte=start)

    if end:
        weather_data = weather_data.filter(recorded_at__date__lte=end)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="weather_report.csv"'

    writer = csv.writer(response)

    writer.writerow([
        "City",
        "Temperature",
        "Humidity",
        "Description",
        "Wind Speed",
        "Recorded At", 
        "Pressure"
    ])

    for item in weather_data.order_by("-recorded_at"):
        writer.writerow([
            item.city,
            item.temperature,
            item.humidity,
            item.description,
            item.wind_speed,
            item.recorded_at,
            item.pressure
        ])

    return response