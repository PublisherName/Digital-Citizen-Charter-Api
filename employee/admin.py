""" Registering the model with the Django admin site. """

from django.contrib import admin
from django import forms
from .models import Employee


class EmployeeForm(forms.ModelForm):
    """
    EmployeeForm class is used to customize the form for the Employee model.
    """

    class Meta:
        """
        Meta class is used to define the model and fields for the form.
        """

        model = Employee
        fields = "__all__"
        widgets = {
            "organization": forms.Select(
                attrs={
                    "onchange": "get_department_for_organization(this.value);",
                    "autocomplete": "off",
                }
            ),
            "department": forms.Select(
                attrs={
                    "onchange": "get_designation_for_department(this.value);",
                    "autocomplete": "off",
                }
            ),
        }


class EmployeeAdmin(admin.ModelAdmin):
    """
    EmployeeAdmin class is used to customize the admin panel for the Employee model.
    """

    form = EmployeeForm

    class Media:
        """
        This class is used to add custom javascript files to the admin panel.
        """

        js = (
            "js/chained/get_department_for_organization.js",
            "js/chained/get_designation_for_department.js",
        )

    list_display = (
        "name",
        "organization",
        "designation",
        "email",
        "contact_no",
        "is_available",
    )


admin.site.register(Employee, EmployeeAdmin)
