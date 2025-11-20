import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.apps import apps

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    - Ne s'exécute PAS pendant les migrations
    - Crée un profil si nouvel utilisateur
    - Répare un profil manquant 
    - Sauvegarde le profil sur update de l'utilisateur
    """

    # Empêche le signal pendant les migrations
    if apps.get_app_config('users').models_module is None:
        return

    # On récupère le modèle UserProfile sans import circulaire
    UserProfile = apps.get_model('users', 'UserProfile')

    if created:
        UserProfile.objects.create(user=instance)
        return

    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        logger.warning(
            f"Profil manquant pour {instance.username}, création automatique."
        )
        UserProfile.objects.create(user=instance)
