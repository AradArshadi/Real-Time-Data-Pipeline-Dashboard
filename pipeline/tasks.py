from celery import shared_task
from .services import fetch_all_cities

@shared_task
def collect_weather_data():
    records = fetch_all_cities()
    return f'Collected {len(records)} weather records'