# Fixes and Run Guide

## What was fixed

### 1. Weather data should not require manual shell insertion

Before, data collection worked only when you manually ran:

```bash
python manage.py shell
from pipeline.services import fetch_all_cities
fetch_all_cities()
```

The project already had a Celery schedule, but automatic collection requires **Celery Beat** and **Celery Worker** to run at the same time.

Use three terminals:

### Terminal 1: Redis

```bash
redis-server
```

On Windows, Redis is often run through Docker or WSL.

### Terminal 2: Celery Worker

```bash
celery -A core worker --loglevel=info --pool=solo
```

### Terminal 3: Celery Beat

```bash
celery -A core beat --loglevel=info
```

Now the task in `core/celery.py` will automatically send the weather collection task every hour.

For a manual one-command test without opening Django shell, use:

```bash
python manage.py collect_weather
```

---

### 2. Logging was added

Logging is now configured in `core/settings.py`.

Logs are written to:

```text
logs/app.log
logs/celery.log
```

The project now logs:

- when dashboard pages are opened
- when CSV export is requested
- when weather collection starts
- success/failure for each city
- OpenWeatherMap API failures
- Celery task start/finish/retry events

---

### 3. API error handling was added

`pipeline/services.py` now uses:

```python
response.raise_for_status()
timeout=10
```

So API failures are handled and logged instead of silently crashing the task.

---

### 4. Template date bug fixed

The dashboard used:

```django
{{ item.created_at }}
```

But the model field is:

```python
recorded_at
```

So it was fixed to:

```django
{{ item.recorded_at|date:"Y-m-d H:i" }}
```

---

### 5. Environment variables added

Secrets were removed from `settings.py`.

Use `.env.example` as a template and create your own `.env` file:

```bash
copy .env.example .env
```

Then edit `.env` and add your real PostgreSQL password and OpenWeatherMap API key.

---

### 6. Showcase architecture graph added

The project now includes:

```text
docs/architecture.png
```

This graph shows the relationship between:

- Celery Beat
- Celery Worker
- service layer
- OpenWeatherMap API
- PostgreSQL database
- Django dashboard
- Django REST Framework API
- settings/logging
