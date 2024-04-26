"""This module is used to define the forms for the organization app."""

from django import forms

from root.utils import download_image_from_url

from .models import Designation, Organization


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
