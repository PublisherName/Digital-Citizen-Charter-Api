""" This file is used to register the models in the admin panel. """

from django.contrib import admin
from .models import Organization, Department, Designation


class OrganizationAdmin(admin.ModelAdmin):
    """
    OrganizationAdmin class is used to customize the admin panel for the Organization model.
    """

    list_display = (
        "name",
        "tag_line",
        "province",
        "district",
        "contact_no",
        "is_active",
    )


class DepartmentAdmin(admin.ModelAdmin):
    """
    DepartmentAdmin class is used to customize the admin panel for the Department model.
    """

    list_display = ("name", "organization", "contact_no", "email", "is_active")


class DesignationAdmin(admin.ModelAdmin):
    """
    DesignationAdmin class is used to customize the admin panel for the Designation model.
    """

    list_display = ("title", "description", "priority", "organization", "department")


admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Designation, DesignationAdmin)
