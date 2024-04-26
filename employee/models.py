from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.db import models

from organization.models import Department, Designation, Organization
from root.utils import UploadToPathAndRename


class Employee(models.Model):
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
        self.validate_designation()

    def save(self, *args, **kwargs):
        self.full_clean()
        try:
            old_employee = Employee.objects.get(pk=self.pk)
            if (
                old_employee.profile_picture
                and old_employee.profile_picture != self.profile_picture
                and default_storage.exists(old_employee.profile_picture.name)
            ):
                default_storage.delete(old_employee.profile_picture.name)
        except Employee.DoesNotExist:
            pass
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.profile_picture and default_storage.exists(self.profile_picture.name):
            default_storage.delete(self.profile_picture.name)
        super().delete(*args, **kwargs)

    def validate_designation(self):
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

    def __str__(self):
        return str(self.name)
