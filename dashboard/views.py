import csv
import logging

from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.dateparse import parse_date

from pipeline.models import City, CollectionRun, WeatherRecord

logger = logging.getLogger(__name__)


def _apply_filters(queryset, start_date, end_date, city_name):
    start = parse_date(start_date) if start_date else None
    end = parse_date(end_date) if end_date else None

    if start:
        queryset = queryset.filter(recorded_at__date__gte=start)

    if end:
        queryset = queryset.filter(recorded_at__date__lte=end)

    if city_name:
        queryset = queryset.filter(city__name__iexact=city_name)

    return queryset


def dashboard_home(request):
    start_date = request.GET.get("start_date", "")
    end_date = request.GET.get("end_date", "")
    selected_city = request.GET.get("city", "")

    records = _apply_filters(
        WeatherRecord.objects.select_related("city", "collection_run"),
        start_date,
        end_date,
        selected_city,
    )

    active_cities = City.objects.filter(is_active=True).order_by("name")

    latest_weather = []
    for city in active_cities:
        latest = records.filter(city=city).order_by("-recorded_at").first()
        if latest:
            latest_weather.append(latest)

    latest_weather.sort(key=lambda item: item.city.name)

    trend_records = list(records.order_by("recorded_at"))
    latest_run = CollectionRun.objects.order_by("-started_at").first()
    latest_record = WeatherRecord.objects.order_by("-recorded_at").first()

    freshness_minutes = None
    freshness_status = "No data"

    if latest_record:
        freshness_minutes = round((timezone.now() - latest_record.recorded_at).total_seconds() / 60)
        freshness_status = "Fresh" if freshness_minutes <= 90 else "Stale"

    context = {
        "cities": active_cities,
        "weather_data": latest_weather,
        "recent_records": records.order_by("-recorded_at")[:50],
        "start_date": start_date,
        "end_date": end_date,
        "selected_city": selected_city,
        "latest_run": latest_run,
        "freshness_minutes": freshness_minutes,
        "freshness_status": freshness_status,
        "total_records": WeatherRecord.objects.count(),
        "active_city_count": active_cities.count(),
        "successful_runs": CollectionRun.objects.filter(status=CollectionRun.Status.SUCCESS).count(),
        "failed_runs": CollectionRun.objects.filter(status__in=[
            CollectionRun.Status.FAILED,
            CollectionRun.Status.PARTIAL_FAILED,
        ]).count(),
        "chart_labels": [item.city.name for item in latest_weather],
        "chart_temperatures": [item.temperature for item in latest_weather],
        "trend_points": [
                {
                    "city": item.city.name,
                    "day": item.recorded_at.strftime("%Y-%m-%d"),
                    "hour": item.recorded_at.strftime("%H:%M"),
                    "hour_number": item.recorded_at.hour,
                    "temperature": item.temperature,
                    "humidity": item.humidity,
                    "pressure": item.pressure,
                }
                for item in trend_records
            ],
    }

    logger.info(
        "Dashboard loaded. city=%s start_date=%s end_date=%s latest=%s",
        selected_city,
        start_date,
        end_date,
        len(latest_weather),
    )

    return render(request, "dashboard/home.html", context)


def export_weather_csv(request):
    start_date = request.GET.get("start_date", "")
    end_date = request.GET.get("end_date", "")
    selected_city = request.GET.get("city", "")

    records = _apply_filters(
        WeatherRecord.objects.select_related("city", "collection_run"),
        start_date,
        end_date,
        selected_city,
    )

    logger.info(
        "CSV export requested. city=%s start_date=%s end_date=%s",
        selected_city,
        start_date,
        end_date,
    )

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="weather_report.csv"'

    writer = csv.writer(response)
    writer.writerow([
        "City",
        "Country",
        "Temperature",
        "Feels Like",
        "Humidity",
        "Description",
        "Wind Speed",
        "Pressure",
        "Cloudiness",
        "Recorded At",
        "Collection Run",
    ])

    for item in records.order_by("-recorded_at"):
        writer.writerow([
            item.city.name,
            item.city.country,
            item.temperature,
            item.feels_like,
            item.humidity,
            item.description,
            item.wind_speed,
            item.pressure,
            item.cloudiness,
            item.recorded_at,
            item.collection_run_id,
        ])

    return response
