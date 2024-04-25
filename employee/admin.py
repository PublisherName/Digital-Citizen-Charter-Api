""" Registering the model with the Django admin site. """

from django.contrib import admin

from .forms import EmployeeForm
from .models import Employee


class EmployeeAdmin(admin.ModelAdmin):
    """
    EmployeeAdmin class is used to customize the admin panel for the Employee model.
    """

    form = EmployeeForm

    list_display = (
        "name",
        "organization",
        "designation",
        "email",
        "contact_no",
        "is_available",
    )


admin.site.register(Employee, EmployeeAdmin)
