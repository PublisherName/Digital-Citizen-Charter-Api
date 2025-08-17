"""This module is used to define the form for the Employee model."""

from django import forms

from root.utils import download_image_from_url

from .models import Department, Designation, Employee, Organization


class EmployeeForm(forms.ModelForm):
    """
    EmployeeForm class is used to customize the form for the Employee model.
    """

    organization = forms.ModelChoiceField(
        queryset=Organization.objects.all(),
        required=True,
        widget=forms.Select(
            attrs={
                "onchange": "get_department_for_organization(this.value);",
                "autocomplete": "off",
            }
        ),
    )

    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=True,
        widget=forms.Select(
            attrs={
                "onchange": "get_designation_for_department(this.value);",
                "autocomplete": "off",
            }
        ),
    )
    profile_picture_url = forms.URLField(required=False)

    def __init__(self, *args, **kwargs):
        """
        Initialize the form and populate organization and department fields for existing instances.
        """
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk and self.instance.designation:
            self.fields["organization"].initial = self.instance.organization
            self.fields["department"].initial = self.instance.department

    class Meta:
        """
        Meta class is used to define the model and fields for the form.
        """

        model = Employee
        fields = [
            "organization",
            "department",
            "designation",
            "name",
            "description",
            "email",
            "contact_no",
            "profile_picture",
            "profile_picture_url",
            "is_available",
        ]

    class Media:
        """
        This class is used to add custom javascript files to the admin panel.
        """

        js = (
            "js/chained/get_department_for_organization.js",
            "js/chained/get_designation_for_department.js",
        )

    def clean(self):
        """
        Validate that the selected designation belongs to the selected department and organization.
        """
        cleaned_data = super().clean()
        organization = cleaned_data.get("organization")
        department = cleaned_data.get("department")
        designation = cleaned_data.get("designation")

        if organization and department and designation:
            if department.organization != organization:
                raise forms.ValidationError(
                    "The selected department does not belong to the selected organization. "
                    f"'{department.name}' belongs to '{department.organization.name}', "
                    f"but you selected '{organization.name}'."
                )

            if designation.department != department:
                raise forms.ValidationError(
                    "The selected designation does not belong to the selected department. "
                    f"'{designation.title}' belongs to '{designation.department.name}', "
                    f"but you selected '{department.name}'."
                )

            if designation.department.organization != organization:
                raise forms.ValidationError(
                    "The selected designation does not belong to the selected organization. "
                    f"'{designation.title}' belongs to "
                    f"'{designation.department.organization.name}', "
                    f"but you selected '{organization.name}'."
                )

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        profile_picture_url = self.cleaned_data.get("profile_picture_url")
        if profile_picture_url:
            filename = f"{instance.name}.jpg"
            image_file = download_image_from_url(profile_picture_url, filename)
            instance.profile_picture.save(filename, image_file, save=False)
        if commit:
            instance.save()
        return instance
