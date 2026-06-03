from django.core.management.base import BaseCommand

from pipeline.services import collect_weather_for_all_cities


class Command(BaseCommand):
    help = "Fetch current weather data for all active cities and save it to the database."

    def handle(self, *args, **options):
        run = collect_weather_for_all_cities()
        self.stdout.write(
            self.style.SUCCESS(
                f"CollectionRun {run.id}: status={run.status}, "
                f"success={run.success_count}, failed={run.failed_count}"
            )
        )
