# Digital Citizen Charter (DCC)

Digital Citizen Charter ( डिजिटल नागरिक वडापत्र ) for Municipalities and government offices.

## Introduction

Digital Citizen Charter (DCC) is a digital version of the Citizen Charter. It is a public declaration of the commitments of the Municipalities and government offices to provide services to the citizens in a time-bound manner. It is a tool for public accountability and transparency in the administration. It is a platform for the citizens to know the services provided by the Municipalities and government offices, the time taken to provide the services, the procedure to avail the services, the fees to be paid for the services, the documents required to avail the services, the officer responsible for providing the services, the time taken to redress the grievances, etc.


## Objective

## Installation

### Traditional Installation

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate
uv sync
```

### Docker Installation (Recommended)

The application is fully containerized using Docker. Choose between development and production setups below.

## Docker Setup

### Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+

### Development Setup

1. **Clone the repository and navigate to the project directory**

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` file with your configuration (see Environment Variables section below).

3. **Copy the docker compose**

   ```bash
   ln -s docker/docker-compose.dev.yml docker-compose.yml
   ```

4. **Start the development environment**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Application: http://localhost:8000
   - Health check: http://localhost:8000/health/

5. **Stop the development environment**
   ```bash
   docker-compose down
   ```

### Production Setup

1. **Create production environment file**
   ```bash
   cp .env.example .env.prod
   ```
   Configure production settings in `.env.prod` (see Environment Variables section).

2. **Deploy with production compose**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d --build
   ```

3. **Monitor application health**
   ```bash
   docker-compose -f docker-compose.prod.yml ps
   ```

4. **View logs**
   ```bash
   docker-compose -f docker-compose.prod.yml logs -f
   ```

### Environment Variables

Create a `.env` file in the project root with the following variables:

#### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key for cryptographic signing | `your-secret-key-here` |
| `DEBUG` | Enable/disable debug mode | `True` (dev), `False` (prod) |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts | `localhost,127.0.0.1` |

#### Optional Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `DATABASE_PATH` | Path to SQLite database file | `/app/data/db.sqlite3` | `/app/data/db.sqlite3` |
| `DJANGO_SUPERUSER_USERNAME` | Auto-create superuser username | - | `admin` |
| `DJANGO_SUPERUSER_EMAIL` | Auto-create superuser email | - | `admin@example.com` |
| `DJANGO_SUPERUSER_PASSWORD` | Auto-create superuser password | - | `secure-password` |

#### Example .env file

```env
# Django Configuration
SECRET_KEY=your-very-secret-key-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database Configuration
DATABASE_PATH=/app/data/db.sqlite3

# Optional: Auto-create superuser (development only)
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=admin123
```

### Docker Commands Reference

#### Development Commands

```bash
# Build and start development environment
docker-compose up --build

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild containers
docker-compose build --no-cache

# Execute commands in running container
docker-compose exec web python manage.py shell
docker-compose exec web python manage.py createsuperuser
```

#### Production Commands

```bash
# Deploy production environment
docker-compose -f docker-compose.prod.yml up -d --build

# Scale application (if needed)
docker-compose -f docker-compose.prod.yml up -d --scale web=3

# Update application
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

# Backup database
docker-compose -f docker-compose.prod.yml exec web cp /app/data/db.sqlite3 /app/backup/
```

### Volume Management

The Docker setup uses named volumes for data persistence:

- **django_db**: SQLite database storage
- **django_media**: User uploaded media files
- **django_static** (production): Collected static files

#### Backup Volumes

```bash
# Backup database volume
docker run --rm -v django_db:/data -v $(pwd):/backup alpine tar czf /backup/db-backup.tar.gz -C /data .

# Backup media volume
docker run --rm -v django_media:/data -v $(pwd):/backup alpine tar czf /backup/media-backup.tar.gz -C /data .
```

#### Restore Volumes

```bash
# Restore database volume
docker run --rm -v django_db:/data -v $(pwd):/backup alpine tar xzf /backup/db-backup.tar.gz -C /data

# Restore media volume
docker run --rm -v django_media:/data -v $(pwd):/backup alpine tar xzf /backup/media-backup.tar.gz -C /data
```

### Troubleshooting

#### Common Issues

1. **Port already in use**
   ```bash
   # Change port in docker-compose.yml or stop conflicting service
   sudo lsof -i :8000
   ```

2. **Permission denied errors**
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER .
   ```

3. **Database migration issues**
   ```bash
   # Run migrations manually
   docker-compose exec web python manage.py migrate
   ```

4. **Static files not loading**
   ```bash
   # Collect static files
   docker-compose exec web python manage.py collectstatic --noinput
   ```

   **Note**: In production, static files are served by WhiteNoise middleware, which is automatically configured. The application uses Django's development static file serving only in DEBUG mode.

#### Health Check

The application includes a health check endpoint at `/health/` that verifies:
- Application is running
- Database connectivity
- Static files availability
- Basic system status

Access it at: http://localhost:8000/health/

## Traditional Migration (Non-Docker)

```bash
python manage.py makemigrations
python manage.py migrate
```

## Traditional Usage (Non-Docker)

```bash
python manage.py runserver
```
