from django.db import models

class WeatherRecord(models.Model):
    city = models.CharField(max_length=100)
    temperature = models.FloatField()
    humidity = models.IntegerField()
    description = models.CharField(max_length=200)
    wind_speed = models.FloatField()
    recorded_at = models.DateTimeField(auto_now_add=True)
    pressure = models.FloatField()

    class Meta:
        ordering = ['-recorded_at']

    def __str__(self):
        return f'{self.city} - {self.temperature}C at {self.recorded_at}'