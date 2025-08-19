#!/bin/sh
uv sync --frozen
uv run python manage.py collectstatic --no-input
uv run python manage.py test -v 3
