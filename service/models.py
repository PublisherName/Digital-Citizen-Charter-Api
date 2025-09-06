from django.core.exceptions import ValidationError
from django.db import models

from root.utils import UploadToPathAndRename


class Service(models.Model):
    """
    Represents a master service that can be offered by organizations.
    """

    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    organizations = models.ManyToManyField(
        "organization.Organization",
        related_name="available_services",
        blank=True,
        help_text="Organizations that are allowed to offer this service. \
        Leave blank if available to all.",
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class ServiceDetail(models.Model):
    """
    Stores the specific details of a service as offered by a particular organization.
    """

    organization = models.ForeignKey(
        "organization.Organization", on_delete=models.CASCADE, related_name="service_details"
    )
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="service_details")
    required_documents = models.TextField(help_text="List of required documents, one per line.")
    process_flow = models.TextField(
        help_text="Describe the process flow for the service, one step per line."
    )
    fees = models.CharField(max_length=100, default="Free", help_text="e.g., 'Rs. 500' or 'Free'")
    timeline = models.CharField(max_length=100, help_text="e.g., '3 working days'")
    responsible_employees = models.ManyToManyField(
        "employee.Employee", blank=True, help_text="Select employees responsible for this service."
    )
    is_active = models.BooleanField(
        default=True, help_text="Is this service currently offered by the organization?"
    )

    def clean(self):
        """
        Custom validation to ensure the organization has access to this service.
        """
        super().clean()
        if self.service and self.organization:
            allowed_orgs = self.service.organizations.all()
            if allowed_orgs.exists() and self.organization not in allowed_orgs:
                raise ValidationError(
                    f"The organization '{self.organization.name}' is not permitted "
                    f"to offer the service '{self.service.name}'."
                )

    def __str__(self):
        return f"{self.service.name} at {self.organization.name}"

    class Meta:
        unique_together = ("organization", "service")
        verbose_name = "Detail"
        verbose_name_plural = "Details"


class SampleDocments(models.Model):
    """
    Represents a sample document template or form for a service detail.
    """

    service_detail = models.ForeignKey(
        ServiceDetail,
        on_delete=models.CASCADE,
        related_name="sample_documents",
        help_text="The service this document is associated with.",
    )
    name = models.CharField(max_length=255, help_text="e.g., 'Application Form'")
    file = models.FileField(upload_to=UploadToPathAndRename("sample_documents"))
    is_active = models.BooleanField(
        default=True, help_text="Is this sample document still releavent?"
    )

    def __str__(self):
        if self.service_detail and self.service_detail.service:
            return f"{self.name} for {self.service_detail.service.name}"
        return self.name

    class Meta:
        verbose_name = "Sample Document"
        verbose_name_plural = "Sample Documents"
