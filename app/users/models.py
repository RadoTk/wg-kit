import logging
from django.db import models, transaction
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from app.orders.models import Country
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel

logger = logging.getLogger(__name__)


class UserProfile(models.Model):
    """
    Modèle représentant le profil utilisateur.
    Ce modèle permet d'associer un profil personnalisé à chaque utilisateur.

    @why: Permet d’étendre le modèle User avec des informations supplémentaires.
    @how: Utilise une relation OneToOne avec le modèle User.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        help_text="L'utilisateur associé à ce profil"
    )
    address = models.CharField(max_length=255, blank=True, help_text="Adresse de l'utilisateur")
    postal_code = models.CharField(max_length=16, blank=True, help_text="Code postal de l'utilisateur")
    country = models.ForeignKey(
        Country, on_delete=models.SET_NULL, null=True, blank=True,
        help_text="Pays de l'utilisateur"
    )
    phone_number = models.CharField(max_length=20, blank=True, help_text="Numéro de téléphone de l'utilisateur")

    def __str__(self):
        """Retourne une représentation lisible du profil."""
        return f"Profil de {self.user.username}"


@receiver(post_save, sender=User)
def manage_user_profile(sender, instance, created, **kwargs):
    """
    Crée ou met à jour automatiquement le profil utilisateur.

    @why: Assure qu’un User a toujours un profil.
    @how: Création automatique en cas de nouvel utilisateur.
    """
    try:
        if created:
            UserProfile.objects.create(user=instance)
        else:
            instance.profile.save()
    except Exception as e:
        logger.error(f"[UserProfile] Échec lors de la gestion du profil de {instance.username}: {str(e)}")
