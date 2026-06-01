from rest_framework import generics
from .models import WeatherRecord
from .serializers import WeatherRecordSerializer

class WeatherListView(generics.ListAPIView):
    serializer_class = WeatherRecordSerializer

    def get_queryset(self):
        queryset = WeatherRecord.objects.all()
        city = self.request.query_params.get('city')
        if city:
            queryset = queryset.filter(city=city)
        return queryset[:100]