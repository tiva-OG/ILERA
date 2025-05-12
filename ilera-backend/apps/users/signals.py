from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User, FarmerProfile, VetProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.is_farmer and not hasattr(instance, "farmer_profile"):
            FarmerProfile.objects.create(user=instance)
        elif instance.is_vet and not hasattr(instance, "vet_profile"):
            VetProfile.objects.create(user=instance)
