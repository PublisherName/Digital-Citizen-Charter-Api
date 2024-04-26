"""This module contains the configuration of the organization app."""

from django.apps import AppConfig


class OrganizationConfig(AppConfig):
    """Configuration of the organization app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "organization"
