import csv
import logging

from django.db.models import OuterRef, Subquery
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.dateparse import parse_date

from pipeline.models import WeatherRecord

logger = logging.getLogger(__name__)


def _apply_date_filters(queryset, start_date, end_date):
    start = parse_date(start_date) if start_date else None
    end = parse_date(end_date) if end_date else None

    if start:
        queryset = queryset.filter(recorded_at__date__gte=start)

    if end:
        queryset = queryset.filter(recorded_at__date__lte=end)

    return queryset


def dashboard_home(request):
    start_date = request.GET.get("start_date", "")
    end_date = request.GET.get("end_date", "")

    weather_data = _apply_date_filters(
        WeatherRecord.objects.all(),
        start_date,
        end_date,
    )

    # Latest record per city, database-portable version.
    latest_ids = (
        weather_data
        .filter(city=OuterRef("city"))
        .order_by("-recorded_at")
        .values("id")[:1]
    )

    latest_weather = (
        WeatherRecord.objects
        .filter(id__in=Subquery(latest_ids))
        .order_by("city")
    )

    chart_labels = [item.city for item in latest_weather]
    chart_temperatures = [item.temperature for item in latest_weather]

    logger.info(
        "Dashboard loaded. start_date=%s end_date=%s records=%s",
        start_date,
        end_date,
        len(chart_labels),
    )

    context = {
        "weather_data": latest_weather,
        "start_date": start_date,
        "end_date": end_date,
        "chart_labels": chart_labels,
        "chart_temperatures": chart_temperatures,
    }

    return render(request, "dashboard/home.html", context)


def export_weather_csv(request):
    start_date = request.GET.get("start_date", "")
    end_date = request.GET.get("end_date", "")

    weather_data = _apply_date_filters(
        WeatherRecord.objects.all(),
        start_date,
        end_date,
    )

    logger.info(
        "CSV export requested. start_date=%s end_date=%s",
        start_date,
        end_date,
    )

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
        "Pressure",
    ])

    for item in weather_data.order_by("-recorded_at"):
        writer.writerow([
            item.city,
            item.temperature,
            item.humidity,
            item.description,
            item.wind_speed,
            item.recorded_at,
            item.pressure,
        ])

    return response
