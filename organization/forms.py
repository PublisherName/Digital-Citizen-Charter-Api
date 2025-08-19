"""This module is used to define the forms for the organization app."""

from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction

from root.utils import download_image_from_url

from .models import Department, Designation, Organization, OrganizationTemplate


class OrganizationForm(forms.ModelForm):
    """
    OrganizationForm class is used to customize the form for the Organization model.
    """

    logo_url = forms.URLField(required=False)
    organization_template = forms.ModelChoiceField(
        queryset=OrganizationTemplate.objects.filter(is_active=True), required=False
    )

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
            "organization_template",
            "is_active",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["organization_template"].widget = forms.HiddenInput()

    def clean_organization_template(self):
        """
        Validate that the selected organization template exists and is active.
        """
        template = self.cleaned_data.get("organization_template")

        if template is None:
            return template
        if not self.fields["organization_template"].queryset.filter(pk=template.pk).exists():
            raise forms.ValidationError(
                "The selected organization template is not available or has been deactivated."
                "Please select a different template or create the organization without a template."
            )

        try:
            template = OrganizationTemplate.objects.get(pk=template.pk, is_active=True)
        except OrganizationTemplate.DoesNotExist:
            raise forms.ValidationError(
                "The selected organization template is not available or has been deactivated. "
                "Please select a different template or create the organization without a template."
            )

        template.refresh_from_db()

        active_departments = template.department_templates.filter(is_active=True)
        if not active_departments.exists():
            raise forms.ValidationError(
                f"The selected template '{template.name}' does not contain any active departments."
                "Please select a different template or create the organization without a template."
            )

        has_active_designations = False
        for dept_template in active_departments:
            if dept_template.designation_templates.filter(is_active=True).exists():
                has_active_designations = True
                break

        if not has_active_designations:
            raise forms.ValidationError(
                f"The template '{template.name}' does not contain any active designations. "
                "Please select a different template or create the organization without a template."
            )

        return template

    def save(self, commit=True):
        instance = super().save(commit=False)
        logo_url = self.cleaned_data.get("logo_url")
        if logo_url:
            image_file = download_image_from_url(logo_url, f"{instance.name}.jpg")
            instance.logo.save(f"{instance.name}.jpg", image_file, save=False)

        is_new_organization = not self.instance.pk
        org_template = self.cleaned_data.get("organization_template")

        if is_new_organization and org_template:
            try:
                with transaction.atomic():
                    instance.save()
                    self._create_from_template(instance, org_template)
            except Exception:
                raise forms.ValidationError(
                    f"Failed to create organization with template '{org_template.name}'. "
                    f"Please try again or contact support if the problem persists."
                )
        return instance

    def _create_from_template(self, organization, org_template):
        """
        Create departments and designations from organization template.
        """

        for department_template in org_template.department_templates.all():
            try:
                department_data = {
                    "organization": organization,
                    "name": department_template.name,
                    "description": department_template.description,
                    "is_active": department_template.is_active,
                    "contact_no": self._get_default_contact_no(department_template),
                    "email": self._get_default_email(department_template, organization),
                }

                department = Department.objects.create(**department_data)

                for designation_template in department_template.designation_templates.all():
                    Designation.objects.create(
                        department=department,
                        title=designation_template.title,
                        description=designation_template.description,
                        priority=designation_template.priority,
                        allow_multiple_employees=designation_template.allow_multiple_employees,
                    )

            except Exception:
                raise

    def _get_default_contact_no(self, department_template):
        """
        Get default contact number for department created from template.
        """
        if hasattr(self, "instance") and self.instance and self.instance.contact_no:
            return self.instance.contact_no
        return "N/A"

    def _get_default_email(self, department_template, organization):
        """
        Get default email for department created from template.
        TODO: Change default email to N/A
        """
        dept_name_clean = department_template.name.lower().replace(" ", "").replace("-", "")
        org_name_clean = organization.name.lower().replace(" ", "").replace("-", "")
        return f"{dept_name_clean}@{org_name_clean}.local"


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
