from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CareSession
from apps.notifications.services import VetcareNotificationDispatcher


@receiver(post_save, sender=CareSession)
def care_session_notification_handler(sender, instance, **kwargs):
    VetcareNotificationDispatcher(instance).dispatch()
