# organization/signals.py

from django.core.files.storage import default_storage
from django.db import transaction
from django.db.models.signals import post_delete, pre_delete
from django.dispatch import receiver

from .models import Organization


@receiver(pre_delete, sender=Organization)
def delete_logo_with_organization(sender, instance, **kwargs):
    if instance.logo and default_storage.exists(instance.logo.name):
        default_storage.delete(instance.logo.name)


@receiver(post_delete, sender=Organization)
def delete_user_with_organization(sender, instance, **kwargs):
    user = instance.user
    if user:
        transaction.on_commit(lambda: user.delete())
