import logging

from celery import shared_task

from .services import fetch_all_cities

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def collect_weather_data(self):
    """Celery task that collects weather data for all configured cities."""
    logger.info("Celery task started: collect_weather_data")

    try:
        records = fetch_all_cities()
        message = f"Collected {len(records)} weather records"
        logger.info("Celery task finished: %s", message)
        return message
    except Exception as exc:
        logger.exception("Celery task failed. Retrying...")
        raise self.retry(exc=exc)
