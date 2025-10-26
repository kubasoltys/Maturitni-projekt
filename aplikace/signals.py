from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import TrenerProfile, HracProfile
from django.apps import apps


User = settings.AUTH_USER_MODEL

@receiver(post_save, sender=User)
def create_profile_for_new_user(sender, instance, created, **kwargs):
    if created:
        # Přeskočí superuživatele
        if instance.is_superuser or instance.is_staff:
            instance.role = 'admin'
            instance.save()
            return

        if instance.role == 'trener':
            TrenerProfile.objects.create(user=instance)
        elif instance.role == 'hrac':
            HracProfile.objects.create(user=instance)
