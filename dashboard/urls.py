from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard_home, name="dashboard_home"),
    path("export/csv/", views.export_weather_csv, name="export_weather_csv"),
]