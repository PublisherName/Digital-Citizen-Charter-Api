FROM python:3.11.8-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    UV_LINK_MODE=copy \
    PYTHONPATH="/app" \
    VIRTUAL_ENV="/app/.venv" \
    PATH="$VIRTUAL_ENV/bin:$PATH"

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    software-properties-common \
    git \
    curl \
    build-essential \
    libsqlite3-mod-spatialite \
    gdal-bin \
    gettext \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.5.26 /uv /uvx /bin/


FROM base AS development

WORKDIR /app

COPY . /app/

RUN uv sync --dev --frozen

ENTRYPOINT ["/app/docker/entrypoint.dev.sh"]


FROM base AS testing

WORKDIR /app

COPY . /app/

RUN uv sync --dev --frozen

ENTRYPOINT ["/app/docker/entrypoint.test.sh"]


FROM base AS production

WORKDIR /app

COPY . /app/

RUN uv sync --frozen --no-dev --all-extras

RUN mkdir -p /app/public/static /app/public/media /app/data

ENTRYPOINT ["/app/docker/entrypoint.prod.sh"]
