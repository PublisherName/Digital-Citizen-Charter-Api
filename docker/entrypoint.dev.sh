#!/bin/sh
uv run python manage.py migrate --no-input
uv run python manage.py collectstatic --no-input
uv run python manage.py runserver 0.0.0.0:8000
