"""This file contains the models for the organization app."""

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.db import models

from root.utils import UploadToPathAndRename

from .choices import PROVINCE_CHOICES

User = get_user_model()


class Organization(models.Model):
    """
    Organization model represents an organization in the system.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, blank=False, null=False)
    tag_line = models.CharField(max_length=200, blank=True, null=False)
    description = models.TextField(blank=False, null=False)

    province = models.CharField(max_length=200, choices=PROVINCE_CHOICES, blank=False, null=False)
    district = models.CharField(max_length=200, blank=False, null=False)
    municipality = models.CharField(max_length=200, blank=False, null=False)
    ward_no = models.CharField(max_length=200, blank=False, null=False)

    contact_no = models.CharField(max_length=15, blank=False, null=False)
    website = models.URLField(max_length=200, blank=False, null=False)
    logo = models.ImageField(upload_to=UploadToPathAndRename("logos"), blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        self.full_clean()
        try:
            old_organization = Organization.objects.get(pk=self.pk)
            if (
                old_organization.logo
                and old_organization.logo != self.logo
                and default_storage.exists(old_organization.logo.name)
            ):
                default_storage.delete(old_organization.logo.name)
        except Organization.DoesNotExist:
            pass
        except Exception as e:
            raise ValidationError(f"An error occurred: {e}")
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.name)


class Department(models.Model):
    """
    Department Model represents the department within the organization.
    """

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, blank=False, null=False)
    description = models.TextField(blank=False)
    contact_no = models.CharField(max_length=20, blank=False, null=False)
    email = models.CharField(max_length=200, blank=False, null=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.name)


class Designation(models.Model):
    """
    Designation Model represents the post / designation of a employee.
    """

    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=False, null=False)
    description = models.TextField(blank=False, null=False)
    priority = models.IntegerField(blank=False, null=False)
    allow_multiple_employees = models.BooleanField(default=False)

    @property
    def organization(self):
        """Return the organization this designation belongs to via department."""
        try:
            if hasattr(self, "department_id") and self.department_id:
                return self.department.organization
            return None
        except (AttributeError, Department.DoesNotExist):
            return None

    def clean(self):
        try:
            has_department = hasattr(self, "department_id") and self.department_id
            if not has_department:
                raise ValidationError("Department is required.")
        except (AttributeError, Department.DoesNotExist):
            raise ValidationError("Department is required.")

    def __str__(self):
        return str(self.title)
