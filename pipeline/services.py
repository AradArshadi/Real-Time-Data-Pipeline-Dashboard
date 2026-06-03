import logging
from datetime import datetime, timezone as datetime_timezone
from typing import Optional

import requests
from django.conf import settings
from django.utils import timezone

from .models import City, CollectionRun, WeatherRecord

logger = logging.getLogger(__name__)


class WeatherAPIError(Exception):
    """Raised when the external weather API cannot be fetched or parsed."""


def ensure_default_cities() -> list[City]:
    """Create configured default cities if they do not exist yet."""
    cities = []

    for city_name in settings.CITIES:
        city, _ = City.objects.get_or_create(name=city_name)
        cities.append(city)

    return cities


def _parse_api_timestamp(timestamp_value):
    if not timestamp_value:
        return None

    return datetime.fromtimestamp(timestamp_value, tz=datetime_timezone.utc)


def fetch_weather(city: City, collection_run: Optional[CollectionRun] = None) -> WeatherRecord:
    """Fetch one city's weather from OpenWeatherMap and save it to the database."""
    if not settings.WEATHER_API_KEY:
        raise WeatherAPIError("WEATHER_API_KEY is missing. Add it to your .env file.")

    params = {
        "q": city.name,
        "appid": settings.WEATHER_API_KEY,
        "units": "metric",
    }

    logger.info("Fetching weather data for city=%s", city.name)

    try:
        response = requests.get(
            settings.WEATHER_API_BASE_URL,
            params=params,
            timeout=settings.WEATHER_API_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as exc:
        raise WeatherAPIError(f"OpenWeatherMap request failed for {city.name}: {exc}") from exc
    except ValueError as exc:
        raise WeatherAPIError(f"OpenWeatherMap returned invalid JSON for {city.name}") from exc

    try:
        city.country = data.get("sys", {}).get("country", city.country or "")
        city.latitude = data.get("coord", {}).get("lat", city.latitude)
        city.longitude = data.get("coord", {}).get("lon", city.longitude)
        city.save(update_fields=["country", "latitude", "longitude", "updated_at"])

        record = WeatherRecord.objects.create(
            city=city,
            collection_run=collection_run,
            temperature=data["main"]["temp"],
            feels_like=data["main"].get("feels_like"),
            humidity=data["main"]["humidity"],
            description=data["weather"][0]["description"],
            wind_speed=data["wind"]["speed"],
            pressure=data["main"]["pressure"],
            cloudiness=data.get("clouds", {}).get("all"),
            api_timestamp=_parse_api_timestamp(data.get("dt")),
            recorded_at=timezone.now(),
        )
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise WeatherAPIError(f"Unexpected OpenWeatherMap response format for {city.name}: {exc}") from exc

    logger.info(
        "Saved weather record id=%s city=%s temperature=%s",
        record.id,
        city.name,
        record.temperature,
    )
    return record


def collect_weather_for_all_cities(task_id: str = "") -> CollectionRun:
    """Run one full collection cycle and record success/failure metadata."""
    cities = ensure_default_cities()
    active_cities = City.objects.filter(is_active=True).order_by("name")

    run = CollectionRun.objects.create(
        task_id=task_id or "",
        status=CollectionRun.Status.RUNNING,
    )

    logger.info("CollectionRun id=%s started for %s active cities", run.id, active_cities.count())

    success_count = 0
    failed_count = 0
    error_messages = []

    for city in active_cities:
        try:
            fetch_weather(city=city, collection_run=run)
            success_count += 1
        except WeatherAPIError as exc:
            failed_count += 1
            error_messages.append(str(exc))
            logger.exception("Failed to collect weather for city=%s", city.name)

    run.success_count = success_count
    run.failed_count = failed_count
    run.finished_at = timezone.now()
    run.error_message = "\n".join(error_messages)

    if success_count > 0 and failed_count == 0:
        run.status = CollectionRun.Status.SUCCESS
    elif success_count > 0 and failed_count > 0:
        run.status = CollectionRun.Status.PARTIAL_FAILED
    else:
        run.status = CollectionRun.Status.FAILED

    run.save(
        update_fields=[
            "success_count",
            "failed_count",
            "finished_at",
            "error_message",
            "status",
        ]
    )

    logger.info(
        "CollectionRun id=%s finished status=%s success=%s failed=%s",
        run.id,
        run.status,
        run.success_count,
        run.failed_count,
    )

    return run


# Backward-compatible helper, so old shell usage still works.
def fetch_all_cities() -> list[WeatherRecord]:
    run = collect_weather_for_all_cities()
    return list(run.weather_records.all())
