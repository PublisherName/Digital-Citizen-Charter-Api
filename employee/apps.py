"""This file contains the configuration for the Employee app."""

from django.apps import AppConfig


class EmployeeConfig(AppConfig):
    """Employee Config class for the employee app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "employee"

    def ready(self):
        import employee.signals
