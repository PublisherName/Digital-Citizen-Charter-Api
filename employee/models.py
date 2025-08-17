from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.db import models

from organization.models import Department, Designation, Organization
from root.utils import UploadToPathAndRename


class Employee(models.Model):
    designation = models.ForeignKey(Designation, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=False)
    email = models.EmailField(unique=True, blank=True, null=True)
    contact_no = models.CharField(max_length=15)
    profile_picture = models.ImageField(
        upload_to=UploadToPathAndRename("profile_pictures"), blank=True, null=True
    )
    is_available = models.BooleanField(default=True)

    @property
    def organization(self):
        """Return the organization this employee belongs to via designation."""
        try:
            return self.designation.department.organization if self.designation else None
        except (AttributeError, models.ObjectDoesNotExist):
            return None

    @property
    def department(self):
        """Return the department this employee belongs to via designation."""
        try:
            return self.designation.department if self.designation else None
        except (AttributeError, models.ObjectDoesNotExist):
            return None

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

    def validate_designation(self):
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
