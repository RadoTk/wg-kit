from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Confession


@receiver(post_save, sender=Confession)
def process_confession(sender, instance, created, **kwargs):
    """
    Process confession after creation - trigger AI analysis
    This follows the pattern from the Posts application documentation where
    confessions trigger AI jobs for:
    - Mention detection
    - Sarcasm scoring
    - Title generation
    - Image generation
    - Moderation checks
    """
    if created:
        # In a real implementation, this would enqueue AI jobs
        # For now, we'll just pass
        pass