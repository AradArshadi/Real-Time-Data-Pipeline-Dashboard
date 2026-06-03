run:
	python manage.py runserver

migrate:
	python manage.py migrate

collect:
	python manage.py collect_weather

worker:
	celery -A core worker --loglevel=info --pool=solo

beat:
	celery -A core beat --loglevel=info

test:
	python manage.py test

docker-up:
	docker compose up --build

docker-down:
	docker compose down
