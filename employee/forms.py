"""This module is used to define the form for the Employee model."""

from django import forms

from root.utils import download_image_from_url

from .models import Employee


class EmployeeForm(forms.ModelForm):
    """
    EmployeeForm class is used to customize the form for the Employee model.
    """

    profile_picture_url = forms.URLField(required=False)

    class Meta:
        """
        Meta class is used to define the model and fields for the form.
        """

        model = Employee
        fields = [
            "name",
            "organization",
            "department",
            "designation",
            "description",
            "email",
            "contact_no",
            "profile_picture",
            "profile_picture_url",
            "is_available",
        ]
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

    class Media:
        """
        This class is used to add custom javascript files to the admin panel.
        """

        js = (
            "js/chained/get_department_for_organization.js",
            "js/chained/get_designation_for_department.js",
        )

    def save(self, commit=True):
        instance = super().save(commit=False)
        profile_picture_url = self.cleaned_data.get("profile_picture_url")
        if profile_picture_url:
            image_file = download_image_from_url(profile_picture_url, f"{instance.name}.jpg")
            instance.profile_picture.save(f"{instance.name}.jpg", image_file, save=False)
        if commit:
            instance.save()
        return instance
