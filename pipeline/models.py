from django.db import models
from django.utils import timezone


class City(models.Model):
    """A city monitored by the weather pipeline."""

    name = models.CharField(max_length=100, unique=True)
    country = models.CharField(max_length=100, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "cities"

    def __str__(self):
        return f"{self.name}, {self.country}" if self.country else self.name


class CollectionRun(models.Model):
    """A single execution of the weather collection pipeline."""

    class Status(models.TextChoices):
        RUNNING = "running", "Running"
        SUCCESS = "success", "Success"
        PARTIAL_FAILED = "partial_failed", "Partial failed"
        FAILED = "failed", "Failed"

    task_id = models.CharField(max_length=255, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.RUNNING,
    )
    started_at = models.DateTimeField(default=timezone.now)
    finished_at = models.DateTimeField(null=True, blank=True)
    success_count = models.PositiveIntegerField(default=0)
    failed_count = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ["-started_at"]

    @property
    def duration_seconds(self):
        if not self.finished_at:
            return None
        return round((self.finished_at - self.started_at).total_seconds(), 2)

    def __str__(self):
        return f"CollectionRun #{self.id} - {self.status}"


class WeatherRecord(models.Model):
    """Weather snapshot collected from an external weather API."""

    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name="weather_records",
    )
    collection_run = models.ForeignKey(
        CollectionRun,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="weather_records",
    )
    temperature = models.FloatField()
    feels_like = models.FloatField(null=True, blank=True)
    humidity = models.IntegerField()
    description = models.CharField(max_length=200)
    wind_speed = models.FloatField()
    pressure = models.FloatField()
    cloudiness = models.IntegerField(null=True, blank=True)
    source = models.CharField(max_length=100, default="OpenWeatherMap")
    api_timestamp = models.DateTimeField(null=True, blank=True)
    recorded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-recorded_at"]
        indexes = [
            models.Index(fields=["city", "-recorded_at"]),
            models.Index(fields=["recorded_at"]),
        ]

    def __str__(self):
        return f"{self.city.name} - {self.temperature}°C at {self.recorded_at}"
