from django.contrib import admin

from .models import City, CollectionRun, WeatherRecord


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "latitude", "longitude", "is_active", "updated_at")
    list_filter = ("is_active", "country")
    search_fields = ("name", "country")


@admin.register(CollectionRun)
class CollectionRunAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "started_at", "finished_at", "success_count", "failed_count", "duration_seconds")
    list_filter = ("status", "started_at")
    search_fields = ("task_id", "error_message")
    readonly_fields = ("duration_seconds",)


@admin.register(WeatherRecord)
class WeatherRecordAdmin(admin.ModelAdmin):
    list_display = ("city", "temperature", "humidity", "pressure", "wind_speed", "recorded_at", "source")
    list_filter = ("city", "source", "recorded_at")
    search_fields = ("city__name", "description")
    date_hierarchy = "recorded_at"
