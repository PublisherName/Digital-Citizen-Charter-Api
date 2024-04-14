""" Registering the model with the Django admin site. """

from django.contrib import admin
from .models import Employee


class EmployeeAdmin(admin.ModelAdmin):
    """
    EmployeeAdmin class is used to customize the admin panel for the Employee model.
    """

    list_display = (
        "name",
        "email",
        "contact_no",
        "designation",
        "is_available",
    )


admin.site.register(Employee, EmployeeAdmin)
