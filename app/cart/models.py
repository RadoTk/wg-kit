import logging
from django.conf import settings
from django.db import models
from app.store.models import StoreProduct
from decimal import Decimal

# Initialisation du logger 
logger = logging.getLogger(__name__)

def calculate_total(items):
    """
    Calcule le total des prix des articles dans un panier.

    @param items: Liste des objets CartItem associés à un panier d'achat.
    @return: La somme des prix des articles. Si une erreur se produit, retourne 0.
    """
    try:
        # Calcul du total en additionnant les prix de chaque article
        return sum(item.get_total_price() for item in items)
    except AttributeError as e:
        # Si un objet dans 'items' n'a pas la méthode 'get_total_price()', on enregistre l'erreur
        logger.error(f"Erreur lors du calcul du total : {e}")
        return Decimal('0.00')  # Retourne 0 en cas d'erreur, pour éviter de planter l'application
    except Exception as e:
        # Pour toute autre erreur, on l'enregistre dans le journal des erreurs
        logger.error(f"Erreur inconnue lors du calcul du total : {e}")
        return Decimal('0.00')  # Retourne 0 pour ne pas interrompre le calcul


class Cart(models.Model):
    """
    Représente un panier d'achat d'un utilisateur.
    
    @why: Permet de stocker les articles d'un panier et de calculer le total.
    @how: Ce modèle est lié à un utilisateur, et contient plusieurs articles (CartItem).
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,  # Utilise le modèle d'utilisateur de Django
        on_delete=models.CASCADE,  # Supprime le panier si l'utilisateur est supprimé
        null=True, 
        blank=True  # Permet de créer un panier sans lier immédiatement un utilisateur
    )
    created_at = models.DateTimeField(auto_now_add=True)  # Date de création du panier
    updated_at = models.DateTimeField(auto_now=True)  # Date de mise à jour du panier

    def get_total(self):
        """
        Calcule le total du panier d'un utilisateur.
        
        @why: Retourne la somme des prix de tous les articles dans le panier.
        @how: Appelle la fonction calculate_total pour effectuer le calcul.
        """
        try:
            return calculate_total(self.items.all())  # Utilise tous les items du panier pour calculer le total
        except Exception as e:
            # Enregistre toute erreur lors du calcul du total
            logger.error(f"Erreur lors du calcul du total du panier pour l'utilisateur {self.user}: {e}")
            return Decimal('0.00')  # Retourne 0 en cas d'erreur


class CartItem(models.Model):
    """
    Représente un article dans le panier d'achat.
    
    @why: Permet de lier un produit à un panier, avec une quantité et un prix.
    @how: Chaque CartItem est lié à un produit et contient des informations comme la quantité et le prix.
    """
    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(StoreProduct, on_delete=models.CASCADE)  # L'article fait référence à un produit
    quantity = models.PositiveIntegerField(default=1)  # Quantité du produit dans le panier
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Prix du produit à l'instant de l'ajout

    def get_total_price(self):
        """
        Calcule le prix total d'un article dans le panier en fonction de sa quantité et de son prix.

        @why: Le total d'un article est calculé en multipliant son prix unitaire par sa quantité.
        @how: Retourne le résultat du calcul du prix total.
        """
        try:
            # Calcule le prix total pour cet article particulier
            return self.price * self.quantity
        except Exception as e:
            # Enregistre l'erreur s'il y a un problème avec le calcul du total
            logger.error(f"Erreur lors du calcul du total pour l'article {self.product.name}: {e}")
            return Decimal('0.00')  # Retourne 0 en cas d'erreur pour ne pas interrompre le processus
