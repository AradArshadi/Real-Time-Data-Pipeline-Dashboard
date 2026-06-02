import logging
from typing import Optional

import requests
from django.conf import settings

from .models import WeatherRecord

logger = logging.getLogger(__name__)


def fetch_weather(city: str) -> Optional[WeatherRecord]:
    """Fetch one city's weather from OpenWeatherMap and save it to the database.

    Returns the created WeatherRecord on success.
    Returns None on failure, while logging the error.
    """
    if not settings.WEATHER_API_KEY:
        logger.error("WEATHER_API_KEY is missing. Add it to your .env file.")
        return None

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": settings.WEATHER_API_KEY,
        "units": "metric",
    }

    logger.info("Fetching weather data for city=%s", city)

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        record = WeatherRecord.objects.create(
            city=city,
            temperature=data["main"]["temp"],
            humidity=data["main"]["humidity"],
            description=data["weather"][0]["description"],
            wind_speed=data["wind"]["speed"],
            pressure=data["main"]["pressure"],
        )

        logger.info(
            "Saved weather record id=%s city=%s temperature=%s",
            record.id,
            record.city,
            record.temperature,
        )
        return record

    except requests.exceptions.RequestException:
        logger.exception("OpenWeatherMap request failed for city=%s", city)
    except (KeyError, IndexError, TypeError, ValueError):
        logger.exception("Unexpected OpenWeatherMap response format for city=%s", city)

    return None


def fetch_all_cities() -> list[WeatherRecord]:
    """Fetch and save weather data for every city in settings.CITIES."""
    logger.info("Starting weather collection for %s cities", len(settings.CITIES))

    records = []

    for city in settings.CITIES:
        record = fetch_weather(city)
        if record is not None:
            records.append(record)

    logger.info(
        "Weather collection finished. success=%s failed=%s",
        len(records),
        len(settings.CITIES) - len(records),
    )

    return records
