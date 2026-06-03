from datetime import datetime, timezone as dt_timezone

import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from pipeline.models import City, CollectionRun, WeatherRecord


CITY_COORDINATES = {
    "London": {"country": "GB", "latitude": 51.5072, "longitude": -0.1276},
    "Berlin": {"country": "DE", "latitude": 52.52, "longitude": 13.405},
    "Istanbul": {"country": "TR", "latitude": 41.0082, "longitude": 28.9784},
    "Tehran": {"country": "IR", "latitude": 35.6892, "longitude": 51.389},
    "Toronto": {"country": "CA", "latitude": 43.6532, "longitude": -79.3832},
}


WEATHER_CODE_DESCRIPTIONS = {
    0: "clear sky",
    1: "mainly clear",
    2: "partly cloudy",
    3: "overcast",
    45: "fog",
    48: "depositing rime fog",
    51: "light drizzle",
    53: "moderate drizzle",
    55: "dense drizzle",
    56: "light freezing drizzle",
    57: "dense freezing drizzle",
    61: "slight rain",
    63: "moderate rain",
    65: "heavy rain",
    66: "light freezing rain",
    67: "heavy freezing rain",
    71: "slight snow fall",
    73: "moderate snow fall",
    75: "heavy snow fall",
    77: "snow grains",
    80: "slight rain showers",
    81: "moderate rain showers",
    82: "violent rain showers",
    85: "slight snow showers",
    86: "heavy snow showers",
    95: "thunderstorm",
    96: "thunderstorm with slight hail",
    99: "thunderstorm with heavy hail",
}


def parse_hour(hour_string):
    dt = datetime.fromisoformat(hour_string)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=dt_timezone.utc)
    return dt


class Command(BaseCommand):
    help = "Backfill hourly historical weather data for all configured cities."

    def add_arguments(self, parser):
        parser.add_argument(
            "--start-date",
            required=True,
            help="Start date in YYYY-MM-DD format, for example 2026-06-01",
        )
        parser.add_argument(
            "--end-date",
            required=True,
            help="End date in YYYY-MM-DD format, for example 2026-06-03",
        )

    def handle(self, *args, **options):
        start_date = options["start_date"]
        end_date = options["end_date"]

        run = CollectionRun.objects.create(
            status=CollectionRun.Status.RUNNING,
            started_at=timezone.now(),
        )

        success_count = 0
        failed_count = 0
        errors = []

        for city_name in settings.CITIES:
            if city_name not in CITY_COORDINATES:
                failed_count += 1
                errors.append(f"Missing coordinates for city: {city_name}")
                self.stdout.write(self.style.ERROR(f"Missing coordinates for {city_name}"))
                continue

            coords = CITY_COORDINATES[city_name]

            city, _ = City.objects.update_or_create(
                name=city_name,
                defaults={
                    "country": coords["country"],
                    "latitude": coords["latitude"],
                    "longitude": coords["longitude"],
                    "is_active": True,
                },
            )

            self.stdout.write(f"Backfilling {city.name} from {start_date} to {end_date}...")

            params = {
                "latitude": city.latitude,
                "longitude": city.longitude,
                "start_date": start_date,
                "end_date": end_date,
                "hourly": ",".join([
                    "temperature_2m",
                    "relative_humidity_2m",
                    "apparent_temperature",
                    "pressure_msl",
                    "cloud_cover",
                    "wind_speed_10m",
                    "weather_code",
                ]),
                "timezone": "UTC",
                "wind_speed_unit": "ms",
            }

            try:
                response = requests.get(
                    "https://archive-api.open-meteo.com/v1/archive",
                    params=params,
                    timeout=30,
                )
                response.raise_for_status()
                data = response.json()
                hourly = data["hourly"]

                times = hourly["time"]

                for index, hour_value in enumerate(times):
                    recorded_at = parse_hour(hour_value)

                    weather_code = hourly["weather_code"][index]
                    description = WEATHER_CODE_DESCRIPTIONS.get(
                        weather_code,
                        f"weather code {weather_code}",
                    )

                    WeatherRecord.objects.update_or_create(
                        city=city,
                        recorded_at=recorded_at,
                        defaults={
                            "collection_run": run,
                            "temperature": hourly["temperature_2m"][index],
                            "feels_like": hourly["apparent_temperature"][index],
                            "humidity": hourly["relative_humidity_2m"][index],
                            "description": description,
                            "wind_speed": hourly["wind_speed_10m"][index],
                            "pressure": hourly["pressure_msl"][index],
                            "cloudiness": hourly["cloud_cover"][index],
                            "source": "Open-Meteo Historical Weather API",
                            "api_timestamp": recorded_at,
                        },
                    )

                success_count += len(times)
                self.stdout.write(
                    self.style.SUCCESS(f"{city.name}: saved/updated {len(times)} hourly records")
                )

            except Exception as exc:
                failed_count += 1
                message = f"{city.name}: {exc}"
                errors.append(message)
                self.stdout.write(self.style.ERROR(message))

        run.success_count = success_count
        run.failed_count = failed_count
        run.finished_at = timezone.now()
        run.error_message = "\n".join(errors)

        if success_count > 0 and failed_count == 0:
            run.status = CollectionRun.Status.SUCCESS
        elif success_count > 0 and failed_count > 0:
            run.status = CollectionRun.Status.PARTIAL_FAILED
        else:
            run.status = CollectionRun.Status.FAILED

        run.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Backfill finished. Run={run.id}, status={run.status}, "
                f"records={success_count}, failed={failed_count}"
            )
        )