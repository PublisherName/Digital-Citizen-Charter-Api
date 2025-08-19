"""
Health check views for container monitoring.
"""

from django.db import connection
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """
    Health check endpoint for container monitoring.
    """
    health_status = {"status": "healthy", "checks": {}}
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        health_status["checks"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful",
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}",
        }

    try:
        from django.conf import settings

        _ = settings.SECRET_KEY
        health_status["checks"]["application"] = {
            "status": "healthy",
            "message": "Application configuration loaded successfully",
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["application"] = {
            "status": "unhealthy",
            "message": f"Application configuration error: {str(e)}",
        }

    status_code = 200 if health_status["status"] == "healthy" else 503

    return JsonResponse(health_status, status=status_code)
