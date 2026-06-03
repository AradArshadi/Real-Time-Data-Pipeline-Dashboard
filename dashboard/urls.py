from django.urls import path

from .views import dashboard_home, export_weather_csv

urlpatterns = [
    path("", dashboard_home, name="dashboard_home"),
    path("export/csv/", export_weather_csv, name="export_weather_csv"),
]
