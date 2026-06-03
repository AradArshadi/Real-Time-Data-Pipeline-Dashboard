# Professional Upgrade Notes

This version is the upgraded portfolio-ready version of the project.

## Major Improvements

1. Docker Compose environment
2. PostgreSQL + Redis + Django + Celery Worker + Celery Beat
3. Professional data model:
   - City
   - WeatherRecord
   - CollectionRun
4. API documentation with Swagger:
   - /api/docs/
   - /api/redoc/
5. More API endpoints:
   - /api/weather/
   - /api/cities/
   - /api/runs/
   - /api/health/
6. Dashboard analytics:
   - latest pipeline run
   - freshness status
   - latest weather per city
   - temperature trend
   - humidity trend
   - pressure trend
   - recent records
   - CSV export
7. Logging:
   - logs/app.log
   - logs/celery.log
8. Tests:
   - model test
   - service test with mocked API
   - dashboard test
   - API test
9. GitHub Actions CI:
   - migration check
   - test run

## Most Important Commands

```bash
python manage.py migrate
python manage.py collect_weather
python manage.py runserver
```

For automatic collection locally:

```bash
celery -A core worker --loglevel=info --pool=solo
celery -A core beat --loglevel=info
```

For Docker:

```bash
docker compose up --build
```

## Existing Old Database Warning

This PRO version changes the database schema. If your old database was created with the MVP version, create a fresh database before running this version.

Clean reset example:

```bash
dropdb -U postgres weather_pipeline
createdb -U postgres weather_pipeline
python manage.py migrate
python manage.py collect_weather
```
