from django.urls import path

from .views import CityListView, CollectionRunListView, HealthCheckView, WeatherListView

urlpatterns = [
    path("weather/", WeatherListView.as_view(), name="weather-list"),
    path("cities/", CityListView.as_view(), name="city-list"),
    path("runs/", CollectionRunListView.as_view(), name="collection-run-list"),
    path("health/", HealthCheckView.as_view(), name="health-check"),
]
