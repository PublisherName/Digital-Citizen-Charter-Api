#!/bin/sh
uv run python manage.py migrate --no-input
uv run python manage.py collectstatic --no-input --clear
uv run gunicorn root.wsgi:application -b 0.0.0.0:8000
