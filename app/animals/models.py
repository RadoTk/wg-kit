from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.models import Orderable
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.images.models import Image


def validate_positive(value):
    if value is None:
        return
    if value < 0:
        raise ValidationError(_('Valeur doit être positive'))


class Animal(models.Model):
    
    SEX_CHOICES = [
        ("M", "Mâle"),
        ("F", "Femelle"),
        ("U", "Inconnu"),
    ]

    CATEGORY_CHOICES = [
        ("dog", "Chien"),
        ("cat", "Chat"),
    ]

    # core fields
    photo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text=_('Photo de l\'animal')
    )
    
    name = models.CharField(max_length=150, verbose_name=_('Nom'))
    breed = models.CharField(max_length=150, verbose_name=_('Race'), blank=True)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='dog')
    age_years = models.PositiveIntegerField(default=0, validators=[validate_positive])
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, validators=[validate_positive])
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, default='U')
    vet_name = models.CharField(max_length=150, blank=True, verbose_name=_('Nom du vétérinaire'))

    # medical info
    allergies = models.TextField(blank=True)
    medical_conditions = models.TextField(blank=True)

    # owner
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='animals',
        verbose_name=_('Utilisateur / Propriétaire')
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Animal'
        verbose_name_plural = 'animals'
        indexes = [
            models.Index(fields=['owner']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

    def clean(self):
        if self.age_years and self.age_years > 100:
            raise ValidationError({'age_years': _('Âge improbable. Vérifiez la valeur.')})
        if self.weight_kg and self.weight_kg > 1000:
            raise ValidationError({'weight_kg': _('Poids improbable. Vérifiez la valeur.')})




