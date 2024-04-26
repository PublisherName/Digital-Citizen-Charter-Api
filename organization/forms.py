"""This module is used to define the forms for the organization app."""

from django import forms

from .models import Designation


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

    class Media:
        """
        This class is used to add custom javascript files to the admin panel.
        """

        js = ("js/chained/get_department_for_organization.js",)
