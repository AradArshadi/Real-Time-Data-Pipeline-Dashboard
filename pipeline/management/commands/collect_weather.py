from django.core.management.base import BaseCommand

from pipeline.services import fetch_all_cities


class Command(BaseCommand):
    help = "Fetch current weather data for all configured cities and save it to the database."

    def handle(self, *args, **options):
        records = fetch_all_cities()
        self.stdout.write(
            self.style.SUCCESS(f"Collected {len(records)} weather records")
        )
