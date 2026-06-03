from rest_framework import serializers

from .models import City, CollectionRun, WeatherRecord


class CitySerializer(serializers.ModelSerializer):
    latest_temperature = serializers.SerializerMethodField()
    latest_recorded_at = serializers.SerializerMethodField()

    class Meta:
        model = City
        fields = [
            "id",
            "name",
            "country",
            "latitude",
            "longitude",
            "is_active",
            "latest_temperature",
            "latest_recorded_at",
        ]

    def get_latest_temperature(self, obj):
        latest = obj.weather_records.order_by("-recorded_at").first()
        return latest.temperature if latest else None

    def get_latest_recorded_at(self, obj):
        latest = obj.weather_records.order_by("-recorded_at").first()
        return latest.recorded_at if latest else None


class CollectionRunSerializer(serializers.ModelSerializer):
    duration_seconds = serializers.ReadOnlyField()

    class Meta:
        model = CollectionRun
        fields = [
            "id",
            "task_id",
            "status",
            "started_at",
            "finished_at",
            "success_count",
            "failed_count",
            "error_message",
            "duration_seconds",
        ]


class WeatherRecordSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source="city.name", read_only=True)
    city_country = serializers.CharField(source="city.country", read_only=True)
    collection_status = serializers.CharField(source="collection_run.status", read_only=True)

    class Meta:
        model = WeatherRecord
        fields = [
            "id",
            "city",
            "city_name",
            "city_country",
            "collection_run",
            "collection_status",
            "temperature",
            "feels_like",
            "humidity",
            "description",
            "wind_speed",
            "pressure",
            "cloudiness",
            "source",
            "api_timestamp",
            "recorded_at",
        ]


class HealthCheckSerializer(serializers.Serializer):
    status = serializers.CharField()
    database = serializers.CharField()
    latest_collection = serializers.DateTimeField(allow_null=True)
    active_cities = serializers.IntegerField()
