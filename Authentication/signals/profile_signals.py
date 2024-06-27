from django.dispatch import receiver
from django.contrib.auth import get_user_model
from Authentication.models import UserProfile
from django.db.models.signals import post_save

User = get_user_model()

@receiver(post_save, sender=User)
def manage_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler to create or update a UserProfile instance whenever a User is created or updated.
    """
    if created:
        UserProfile.objects.create(user=instance)
    else:
        profile, _ = UserProfile.objects.get_or_create(user=instance)
        profile.full_name = getattr(instance, 'full_name', profile.full_name)
        profile.username = getattr(instance, 'username', profile.username)
        profile.save()
