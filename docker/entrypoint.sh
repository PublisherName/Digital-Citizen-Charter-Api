#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[ENTRYPOINT]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[ENTRYPOINT]${NC} $1"
}

print_error() {
    echo -e "${RED}[ENTRYPOINT]${NC} $1"
}

wait_for_db() {
    print_status "Checking database connectivity..."

    DB_DIR=$(dirname "${DATABASE_PATH:-/app/data/db.sqlite3}")

    if [ ! -d "$DB_DIR" ]; then
        print_status "Creating database directory: $DB_DIR"
        mkdir -p "$DB_DIR"
    fi

    if [ ! -w "$DB_DIR" ]; then
        print_error "Database directory is not writable: $DB_DIR"
        exit 1
    fi

    print_status "Database directory is ready"
}

run_migrations() {
    print_status "Running database migrations..."

    if python manage.py migrate --check > /dev/null 2>&1; then
        print_status "Database is up to date"
    else
        print_status "Applying database migrations..."
        if python manage.py migrate; then
            print_status "Database migrations completed successfully"
        else
            print_error "Database migrations failed"
            exit 1
        fi
    fi
}

collect_static() {
    print_status "Collecting static files..."

    if python manage.py collectstatic --noinput --clear; then
        print_status "Static files collected successfully"
    else
        print_error "Static files collection failed"
        exit 1
    fi
}

create_superuser() {
    if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
        print_status "Creating superuser..."

        if python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
exists = User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists();
print('EXISTS' if exists else 'NOT_EXISTS')
" | grep -q "EXISTS"; then
            print_warning "Superuser '$DJANGO_SUPERUSER_USERNAME' already exists, skipping creation"
        else
            if python manage.py createsuperuser --noinput; then
                print_status "Superuser created successfully"
            else
                print_error "Failed to create superuser"
                exit 1
            fi
        fi
    else
        print_status "Superuser environment variables not provided, skipping superuser creation"
    fi
}

validate_environment() {
    print_status "Validating environment configuration..."

    if [ -z "$SECRET_KEY" ]; then
        print_error "SECRET_KEY environment variable is required"
        exit 1
    fi

    if [ -n "$DEBUG" ] && [ "$DEBUG" != "True" ] && [ "$DEBUG" != "False" ] && [ "$DEBUG" != "1" ] && [ "$DEBUG" != "0" ]; then
        print_warning "DEBUG should be 'True', 'False', '1', or '0'. Current value: '$DEBUG'"
    fi

    print_status "Environment validation completed"
}

main() {
    print_status "Starting Django application initialization..."

    validate_environment

    wait_for_db

    run_migrations

    collect_static

    create_superuser

    print_status "Initialization completed successfully"

    print_status "Starting Django application with command: $*"
    exec "$@"
}

trap 'print_error "An error occurred during initialization. Exiting..."; exit 1' ERR

main "$@"
