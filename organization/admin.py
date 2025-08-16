"""This file is used to register the models in the admin panel."""

from django.contrib import admin

from .forms import DesignationForm, OrganizationForm
from .models import Department, Designation, Organization


@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    """
    DesignationAdmin class is used to customize the admin panel for the Designation model.
    """

    form = DesignationForm

    list_display = ("title", "description", "priority", "organization", "department")


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """
    OrganizationAdmin class is used to customize the admin panel for the Organization model.
    """

    form = OrganizationForm

    list_display = (
        "name",
        "tag_line",
        "province",
        "district",
        "contact_no",
        "is_active",
    )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """
    DepartmentAdmin class is used to customize the admin panel for the Department model.
    """

    list_display = ("name", "organization", "contact_no", "email", "is_active")
