FROM python:3.11.8-slim as base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    software-properties-common \
    git \
    curl \
    build-essential \
    libsqlite3-mod-spatialite \
    gdal-bin \
    gettext

ENV UV_LINK_MODE=copy \
    PYTHONPATH="/app" \
    VIRTUAL_ENV="/app/.venv"

ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY --from=ghcr.io/astral-sh/uv:0.5.26 /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock* ./



FROM base as development

RUN uv sync --dev

COPY . .

EXPOSE 8000

CMD ["uv", "run", "python","manage.py", "runserver", "0.0.0.0:8000"]



FROM base as production

RUN uv sync --no-dev

COPY . .

RUN mkdir -p /app/public/static /app/public/media /app/data

COPY docker/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh


EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["uv", "run", "gunicorn", "--bind", "0.0.0.0:8000", "root.wsgi:application"]
