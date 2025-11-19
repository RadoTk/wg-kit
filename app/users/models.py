from django.db import models
from django.contrib.auth.models import User
from app.orders.models import Country

from django.db.models.signals import post_save
from django.dispatch import receiver



class UserProfile(models.Model):
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



@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
