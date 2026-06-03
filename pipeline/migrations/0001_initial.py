# Generated manually for the professional portfolio version.

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="City",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, unique=True)),
                ("country", models.CharField(blank=True, max_length=100)),
                ("latitude", models.FloatField(blank=True, null=True)),
                ("longitude", models.FloatField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["name"],
                "verbose_name_plural": "cities",
            },
        ),
        migrations.CreateModel(
            name="CollectionRun",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("task_id", models.CharField(blank=True, max_length=255)),
                ("status", models.CharField(choices=[("running", "Running"), ("success", "Success"), ("partial_failed", "Partial failed"), ("failed", "Failed")], default="running", max_length=20)),
                ("started_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("finished_at", models.DateTimeField(blank=True, null=True)),
                ("success_count", models.PositiveIntegerField(default=0)),
                ("failed_count", models.PositiveIntegerField(default=0)),
                ("error_message", models.TextField(blank=True)),
            ],
            options={
                "ordering": ["-started_at"],
            },
        ),
        migrations.CreateModel(
            name="WeatherRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("temperature", models.FloatField()),
                ("feels_like", models.FloatField(blank=True, null=True)),
                ("humidity", models.IntegerField()),
                ("description", models.CharField(max_length=200)),
                ("wind_speed", models.FloatField()),
                ("pressure", models.FloatField()),
                ("cloudiness", models.IntegerField(blank=True, null=True)),
                ("source", models.CharField(default="OpenWeatherMap", max_length=100)),
                ("api_timestamp", models.DateTimeField(blank=True, null=True)),
                ("recorded_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("city", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="weather_records", to="pipeline.city")),
                ("collection_run", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="weather_records", to="pipeline.collectionrun")),
            ],
            options={
                "ordering": ["-recorded_at"],
                "indexes": [
                    models.Index(fields=["city", "-recorded_at"], name="pipeline_we_city_i_21f80c_idx"),
                    models.Index(fields=["recorded_at"], name="pipeline_we_recorde_f3f3f2_idx"),
                ],
            },
        ),
    ]
