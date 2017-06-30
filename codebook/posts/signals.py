from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Answer
from profiles.utils import perform_reputation_check


@receiver(post_save, sender=Answer)
def update_reputation(sender, instance, created, **kwargs):
    if created:
        return
    user = instance.user
    profile = user.profile
    reputation = perform_reputation_check(user)
    if profile.reputation != reputation:
        profile.reputation = reputation
        profile.save()

