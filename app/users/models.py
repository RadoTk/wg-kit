from asyncio.log import logger
from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import post_save
from django.dispatch import receiver

from wagtail.models import Page
from wagtail.admin.panels import FieldPanel

from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect


class Country(models.Model):
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=10, blank=True)

    class Meta:
        verbose_name = "Pays"

    def __str__(self):
        return self.name
    

class UserProfile(models.Model):
    """
    Modèle représentant le profil utilisateur.
    Ce modèle permet d'associer un profil personnalisé à chaque utilisateur, avec des informations comme l'adresse, le code postal, le pays, et le numéro de téléphone.

    @why: Assurer qu'un utilisateur puisse avoir un profil distinct contenant des informations supplémentaires au-delà de celles du modèle User.
    @how: Chaque utilisateur pourra avoir un profil qui est relié à lui via une relation OneToOne.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    phone_number = models.CharField(max_length=20, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(
        choices=[("M", "Homme"), ("F", "Femme"), ("O", "Autre")],
        max_length=1,
        blank=True
    )

    default_billing_address = models.ForeignKey(
        "users.Address",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="billing_profiles",
    )

    default_shipping_address = models.ForeignKey(
        "users.Address",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="shipping_profiles",
    )

    def __str__(self):
        """
        Retourne une représentation en chaîne de caractères du profil utilisateur.
        
        @why: Permet d'afficher le profil utilisateur de manière lisible.
        @how: Affiche "Profil de {username}" dans l'administration Django.
        """
        return f"Profil de {self.user.username}"


class Address(models.Model):
    ADDRESS_TYPES = [
        ("shipping", "Adresse de livraison"),
        ("billing", "Adresse de facturation"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    address_type = models.CharField(max_length=20, choices=ADDRESS_TYPES)

    full_name = models.CharField(max_length=255)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.PROTECT)

    phone_number = models.CharField(max_length=20, blank=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.full_name} - {self.address_type}"



