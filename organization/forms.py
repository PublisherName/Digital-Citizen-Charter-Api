"""This module is used to define the forms for the organization app."""

from django import forms

from root.utils import download_image_from_url

from .models import Department, Designation, Organization


class OrganizationForm(forms.ModelForm):
    """
    OrganizationForm class is used to customize the form for the Organization model.
    """

    logo_url = forms.URLField(required=False)

    class Meta:
        """
        Meta class is used to define the model and fields for the form.
        """

        model = Organization

        fields = [
            "user",
            "name",
            "tag_line",
            "description",
            "province",
            "district",
            "municipality",
            "ward_no",
            "contact_no",
            "website",
            "logo",
            "logo_url",
            "is_active",
        ]

    def save(self, commit=True):
        instance = super().save(commit=False)
        logo_url = self.cleaned_data.get("logo_url")
        if logo_url:
            image_file = download_image_from_url(logo_url, f"{instance.name}.jpg")
            instance.logo.save(f"{instance.name}.jpg", image_file, save=False)
        if commit:
            instance.save()
        return instance


class DesignationForm(forms.ModelForm):
    """
    DesignationForm class is used to customize the form for the Designation model.
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

    class Meta:
        """
        Meta class is used to define the model and fields for the form.
        """

        model = Designation
        fields = [
            "organization",
            "department",
            "title",
            "description",
            "priority",
            "allow_multiple_employees",
        ]

    def __init__(self, *args, **kwargs):
        """
        Initialize the form and set the organization field value if editing existing designation.
        """
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.department:
            self.fields["organization"].initial = self.instance.department.organization

    def clean(self):
        """
        Validate that the selected department belongs to the selected organization.
        """
        cleaned_data = super().clean()
        organization = cleaned_data.get("organization")
        department = cleaned_data.get("department")

        if organization and department:
            if department.organization != organization:
                raise forms.ValidationError(
                    {
                        "department": (
                            f"The selected department '{department.name}' does not belong to "
                            f"the selected organization '{organization.name}'. Please select a "
                            f"department that belongs to '{organization.name}'."
                        )
                    }
                )
        elif organization and not department:
            raise forms.ValidationError(
                {
                    "department": (
                        f"Please select a department from the organization '{organization.name}'."
                    )
                }
            )
        elif department and not organization:
            cleaned_data["organization"] = department.organization

        return cleaned_data

    def save(self, commit=True):
        """
        Save the designation without saving the organization field.
        """
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance

    class Media:
        """
        This class is used to add custom javascript files to the admin panel.
        """

        js = ("js/chained/get_department_for_organization.js",)
