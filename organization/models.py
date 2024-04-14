""" This file contains the models for the organization app. """

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from root.utils import UploadToPathAndRename
from .choices import PROVINCE_CHOICES


class Organization(models.Model):
    """
    Organization model represents an organization in the system.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, blank=False, null=False)
    tag_line = models.CharField(max_length=200, blank=True, null=False)
    description = models.CharField(max_length=200, blank=False, null=False)

    province = models.CharField(
        max_length=200, choices=PROVINCE_CHOICES, blank=False, null=False
    )
    district = models.CharField(max_length=200, blank=False, null=False)
    municipality = models.CharField(max_length=200, blank=False, null=False)
    ward_no = models.CharField(max_length=200, blank=False, null=False)

    contact_no = models.CharField(max_length=15, blank=False, null=False)
    website = models.CharField(max_length=200, blank=False, null=False)
    logo = models.ImageField(
        upload_to=UploadToPathAndRename("logos"), blank=True, null=True
    )
    is_active = models.BooleanField(default=True)

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

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=False, null=False)
    description = models.TextField(blank=False, null=False)
    priority = models.IntegerField(blank=False, null=False)

    def clean(self):
        if self.organization != self.department.organization:
            raise ValidationError(
                f"Your Organization doesn't have {self.department} department."
            )

    def __str__(self):
        return str(self.title)
