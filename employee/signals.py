# employee/signals.py

from django.core.files.storage import default_storage
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .models import Employee


@receiver(pre_delete, sender=Employee)
def delete_profile_picture_with_employee(sender, instance, **kwargs):
    if instance.profile_picture and default_storage.exists(instance.profile_picture.name):
        default_storage.delete(instance.profile_picture.name)
