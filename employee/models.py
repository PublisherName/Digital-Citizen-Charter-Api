"""This file contains the model for the Employee"""

from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.db import models

from organization.models import Department, Designation, Organization
from root.utils import UploadToPathAndRename


class Employee(models.Model):
    """
    Employee model represents an employee in the system.
    """

    name = models.CharField(max_length=200)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    designation = models.ForeignKey(Designation, on_delete=models.CASCADE)
    description = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(unique=True)
    contact_no = models.CharField(max_length=15)
    profile_picture = models.ImageField(
        upload_to=UploadToPathAndRename("profile_pictures"), blank=True, null=True
    )
    is_available = models.BooleanField(default=True)

    def clean(self):
        """
        Overriding the clean method to validate the designation.
        """
        if self.department.organization != self.organization:
            raise ValidationError("Designation's department must match the selected organization.")

        if self.designation.department != self.department:
            raise ValidationError("Designation's must match the selected department.")

        if not self.designation.allow_multiple_employees and (
            Employee.objects.filter(designation=self.designation)
            .exclude(pk=self.pk if self.pk else None)
            .exists()
        ):
            raise ValidationError(
                f"The employee has already been assigned to the {self.designation} role."
            )

    def save(self, *args, **kwargs):
        """
        Overriding the save method to set the organization and department based on the designation.
        """
        self.full_clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Overriding the delete method to delete the profile picture from the storage.
        """

        if self.profile_picture and default_storage.exists(self.profile_picture.name):
            default_storage.delete(self.profile_picture.name)

        super().delete(*args, **kwargs)

    def __str__(self):
        return str(self.name)
