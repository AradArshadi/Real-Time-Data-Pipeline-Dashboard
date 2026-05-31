import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'collect-weather-every-hour': {
        'task': 'pipeline.tasks.collect_weather_data',
        'schedule': crontab(minute=0, hour='*'),
    },
}