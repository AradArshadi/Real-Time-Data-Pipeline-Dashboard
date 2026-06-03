import logging

from celery import shared_task

from .services import collect_weather_for_all_cities

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def collect_weather_data(self):
    """Celery task that collects weather data for all active cities."""
    logger.info("Celery task started: collect_weather_data task_id=%s", self.request.id)

    try:
        run = collect_weather_for_all_cities(task_id=self.request.id)
        message = (
            f"CollectionRun {run.id}: status={run.status}, "
            f"success={run.success_count}, failed={run.failed_count}"
        )
        logger.info("Celery task finished: %s", message)
        return message
    except Exception as exc:
        logger.exception("Celery task crashed before CollectionRun finished. Retrying...")
        raise self.retry(exc=exc)
