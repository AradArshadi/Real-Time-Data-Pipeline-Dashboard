from django.db import connection
from django.utils.dateparse import parse_date
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import City, CollectionRun, WeatherRecord
from .serializers import (
    CitySerializer,
    CollectionRunSerializer,
    HealthCheckSerializer,
    WeatherRecordSerializer,
)


class CityListView(generics.ListAPIView):
    """List monitored cities."""

    serializer_class = CitySerializer
    queryset = City.objects.all()


@extend_schema(
    parameters=[
        OpenApiParameter(name="city", description="Filter by city name, e.g. Berlin", required=False, type=str),
        OpenApiParameter(name="start_date", description="Start date in YYYY-MM-DD format", required=False, type=str),
        OpenApiParameter(name="end_date", description="End date in YYYY-MM-DD format", required=False, type=str),
    ]
)
class WeatherListView(generics.ListAPIView):
    """List weather records with optional filters."""

    serializer_class = WeatherRecordSerializer

    def get_queryset(self):
        queryset = (
            WeatherRecord.objects
            .select_related("city", "collection_run")
            .order_by("-recorded_at")
        )

        city = self.request.query_params.get("city")
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")

        if city:
            queryset = queryset.filter(city__name__iexact=city)

        start = parse_date(start_date) if start_date else None
        end = parse_date(end_date) if end_date else None

        if start:
            queryset = queryset.filter(recorded_at__date__gte=start)

        if end:
            queryset = queryset.filter(recorded_at__date__lte=end)

        return queryset


class CollectionRunListView(generics.ListAPIView):
    """List pipeline collection runs."""

    serializer_class = CollectionRunSerializer
    queryset = CollectionRun.objects.all()


class HealthCheckView(APIView):
    """Simple health endpoint for monitoring and deployment checks."""

    @extend_schema(responses=HealthCheckSerializer)
    def get(self, request):
        database_status = "ok"

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        except Exception:
            database_status = "error"

        latest_collection = CollectionRun.objects.order_by("-started_at").first()

        data = {
            "status": "ok" if database_status == "ok" else "degraded",
            "database": database_status,
            "latest_collection": latest_collection.started_at if latest_collection else None,
            "active_cities": City.objects.filter(is_active=True).count(),
        }

        serializer = HealthCheckSerializer(data)
        return Response(serializer.data)
