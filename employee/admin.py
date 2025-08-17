"""Registering the model with the Django admin site."""

from django.contrib import admin

from .forms import EmployeeForm
from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """
    EmployeeAdmin class is used to customize the admin panel for the Employee model.
    """

    form = EmployeeForm

    list_display = (
        "name",
        "organization",
        "department",
        "designation",
        "email",
        "contact_no",
        "is_available",
    )

    list_filter = (
        "designation__department__organization",
        "designation__department",
        "designation",
        "is_available",
    )

    search_fields = (
        "name",
        "email",
        "designation__name",
        "designation__department__name",
        "designation__department__organization__name",
    )

    list_select_related = ("designation__department__organization",)
