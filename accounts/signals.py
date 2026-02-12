from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=Profile)
def sync_profile_role_to_group(sender, instance: Profile, **kwargs):
    """
    Keep a simple mapping between Profile.role and Django auth Group membership.
    """
    try:
        group, _ = Group.objects.get_or_create(name="service_center")
        if instance.role == Profile.ROLE_SERVICE_CENTER:
            instance.user.groups.add(group)
        else:
            instance.user.groups.remove(group)
    except Exception:
        return

