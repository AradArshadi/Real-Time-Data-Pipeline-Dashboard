from unittest.mock import Mock, patch

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import City, CollectionRun, WeatherRecord
from .services import collect_weather_for_all_cities, fetch_weather


class WeatherModelTests(TestCase):
    def test_weather_record_string_contains_city_and_temperature(self):
        city = City.objects.create(name="Berlin", country="DE")
        record = WeatherRecord.objects.create(
            city=city,
            temperature=25.5,
            humidity=45,
            description="clear sky",
            wind_speed=3.2,
            pressure=1012,
        )

        self.assertIn("Berlin", str(record))
        self.assertIn("25.5", str(record))


class WeatherServiceTests(TestCase):
    @override_settings(WEATHER_API_KEY="test-key", CITIES=["Berlin"])
    @patch("pipeline.services.requests.get")
    def test_fetch_weather_creates_record(self, mock_get):
        city = City.objects.create(name="Berlin")

        mock_response = Mock()
        mock_response.json.return_value = {
            "main": {
                "temp": 23.4,
                "feels_like": 22.9,
                "humidity": 50,
                "pressure": 1011,
            },
            "weather": [{"description": "clear sky"}],
            "wind": {"speed": 2.5},
            "clouds": {"all": 10},
            "sys": {"country": "DE"},
            "coord": {"lat": 52.52, "lon": 13.405},
            "dt": 1710000000,
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        record = fetch_weather(city)

        self.assertEqual(record.city.name, "Berlin")
        self.assertEqual(record.temperature, 23.4)
        self.assertEqual(record.humidity, 50)

    @override_settings(WEATHER_API_KEY="test-key", CITIES=["Berlin"])
    @patch("pipeline.services.requests.get")
    def test_collect_weather_for_all_cities_creates_collection_run(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            "main": {
                "temp": 23.4,
                "feels_like": 22.9,
                "humidity": 50,
                "pressure": 1011,
            },
            "weather": [{"description": "clear sky"}],
            "wind": {"speed": 2.5},
            "clouds": {"all": 10},
            "sys": {"country": "DE"},
            "coord": {"lat": 52.52, "lon": 13.405},
            "dt": 1710000000,
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        run = collect_weather_for_all_cities()

        self.assertEqual(run.status, CollectionRun.Status.SUCCESS)
        self.assertEqual(run.success_count, 1)
        self.assertEqual(run.failed_count, 0)
        self.assertEqual(WeatherRecord.objects.count(), 1)


class APITests(TestCase):
    def setUp(self):
        self.client = Client()
        self.city = City.objects.create(name="Berlin", country="DE")
        self.run = CollectionRun.objects.create(
            status=CollectionRun.Status.SUCCESS,
            finished_at=timezone.now(),
            success_count=1,
        )
        WeatherRecord.objects.create(
            city=self.city,
            collection_run=self.run,
            temperature=25,
            humidity=40,
            description="sunny",
            wind_speed=1.5,
            pressure=1010,
        )

    def test_weather_api_returns_records(self):
        response = self.client.get("/api/weather/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Berlin")

    def test_city_api_returns_cities(self):
        response = self.client.get("/api/cities/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Berlin")

    def test_health_check_returns_ok(self):
        response = self.client.get("/api/health/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ok")


class DashboardTests(TestCase):
    def setUp(self):
        self.client = Client()
        city = City.objects.create(name="Berlin", country="DE")
        WeatherRecord.objects.create(
            city=city,
            temperature=25,
            humidity=40,
            description="sunny",
            wind_speed=1.5,
            pressure=1010,
        )

    def test_dashboard_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Real-Time Weather Data Pipeline")

    def test_csv_export_loads(self):
        response = self.client.get(reverse("export_weather_csv"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertContains(response, "Berlin")
