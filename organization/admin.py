""" This file is used to register the models in the admin panel. """

from django.contrib import admin
from django import forms
from .models import Organization, Department, Designation


class DesignationForm(forms.ModelForm):
    """
    DesignationForm class is used to customize the form for the Designation model.
    """

    class Meta:
        """
        Meta class is used to define the model and fields for the form.
        """

        model = Designation
        fields = "__all__"
        widgets = {
            "organization": forms.Select(
                attrs={
                    "onchange": "get_department_for_organization(this.value);",
                    "autocomplete": "off",
                }
            )
        }


class DesignationAdmin(admin.ModelAdmin):
    """
    DesignationAdmin class is used to customize the admin panel for the Designation model.
    """

    form = DesignationForm

    class Media:
        """
        This class is used to add custom javascript files to the admin panel.
        """

        js = ("js/chained/get_department_for_organization.js",)

    list_display = ("title", "description", "priority", "organization", "department")


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


admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Designation, DesignationAdmin)
