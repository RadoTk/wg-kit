from asyncio.log import logger
from django.db.models import Sum, F
from decimal import Decimal
from collections.abc import Generator
from django.conf import settings
from django.http import HttpRequest
from django.shortcuts import redirect
from app.store.models import StoreProduct
from .models import Cart as CartModel, CartItem


class Cart:
    """
    @why: Classe représentant un panier d'achat. Elle gère les paniers en session et en base de données.
    @how: Permet d'ajouter, supprimer, vider les produits et de calculer les totaux du panier.
    """

    def __init__(self, request: HttpRequest) -> None:
        """
        @why: Initialisation du panier avec gestion de l'authentification.
        @how: Si l'utilisateur est connecté, utilise un panier en base de données. Sinon, utilise un panier en session.
        """
        self.session = request.session
        self.user = getattr(request, "user", None)
        self.session_cart = self.session.get(settings.CART_SESSION_ID, {})

        if self.user and self.user.is_authenticated:
            # Récupération ou création du panier en base de données
            self.db_cart, _ = CartModel.objects.get_or_create(user=self.user)
            if self.session_cart:
                # Fusionner les produits de la session dans la base de données
                self.merge_session_cart()
        else:
            # Utilisation du panier en session uniquement
            self.db_cart = None

    def add(self, product: StoreProduct, quantity: int = 1, replace_quantity=False) -> None:
        """
        @why: Ajouter ou mettre à jour un produit dans le panier.
        @how: Si le panier est en base de données, mettre à jour ou créer l'article. Sinon, mettre à jour la session.
        """
        if self.db_cart:
            # Panier en base de données
            try:
                item, isCreated = CartItem.objects.get_or_create(
                    cart=self.db_cart,
                    product=product,
                    defaults={"price": product.price, "quantity": quantity}
                )
                if not isCreated:
                    # Si l'article existe déjà, on met à jour la quantité et le prix
                    item.quantity = quantity if replace_quantity else item.quantity + quantity
                    item.price = product.price
                    item.save()
            except Exception as e:
                # En cas d'erreur lors de l'ajout ou mise à jour dans la base de données
                logger.error(f"Erreur lors de l'ajout du produit dans le panier: {e}")
                # Redirection ou retour d'information à l'utilisateur
                return redirect("/")
        else:
            # Panier en session
            try:
                product_id = str(product.id)
                existing_item = self.session_cart.get(product_id)

                if existing_item:
                    # Si le produit existe déjà, on ajuste la quantité
                    if replace_quantity:
                        new_quantity = quantity
                    else:
                        new_quantity = existing_item["quantity"] + quantity
                else:
                    # Si le produit n'existe pas dans le panier de session, on l'ajoute
                    new_quantity = quantity

                # Mise à jour du panier en session
                self.session_cart[product_id] = {
                    "product_title": product.title,
                    "product_id": product_id,
                    "quantity": new_quantity,
                    "price": str(product.price),  # Conversion du prix en chaîne
                }

                self.save_session()
            except Exception as e:
                # Gestion des erreurs en session
                logger.error(f"Erreur lors de l'ajout du produit dans le panier de session: {e}")
                return redirect("/")

    def remove(self, product: StoreProduct) -> None:
        """
        @why: Supprimer un produit du panier.
        @how: Si le panier est en base de données, on supprime l'article de la DB. Sinon, on retire de la session.
        """
        try:
            if self.db_cart:
                CartItem.objects.filter(cart=self.db_cart, product=product).delete()
            else:
                # Retirer du panier en session
                self.session_cart.pop(str(product.id), None)
                self.save_session()
        except Exception as e:
            # Gestion des erreurs de suppression
            logger.error(f"Erreur lors de la suppression du produit: {e}")
            return redirect("/")

    def clear(self) -> None:
        """
        @why: Vider le panier.
        @how: Supprimer tous les articles du panier, soit en base de données, soit en session.
        """
        try:
            if self.db_cart:
                self.db_cart.items.all().delete()
            else: self.clear_session()
        except Exception as e:
            # Gestion des erreurs de vidage du panier
            logger.error(f"Erreur lors du vidage du panier: {e}")
            return redirect("/")

    def merge_session_cart(self) -> None:
        """
        @why: Fusionner le panier de la session avec celui en base de données.
        @how: Ajouter les articles de la session à la base de données et vider la session.
        """
        try:
            # Récupérer les produits de la session
            products_in_session = StoreProduct.objects.filter(id__in=self.session_cart.keys())
            for product in products_in_session:
                quantity_in_session = self.session_cart[str(product.id)]["quantity"]
                self.add(product, quantity_in_session)  # Ajouter chaque produit de la session à la DB

            self.clear_session()
        except Exception as e:
            # Gestion des erreurs de fusion
            logger.error(f"Erreur lors de la fusion du panier de session: {e}")
            return redirect("/")

    def save_session(self) -> None:
        """
        @why: Sauvegarder l'état du panier en session.
        @how: Met à jour la session avec les articles du panier.
        """
        try:
            self.session[settings.CART_SESSION_ID] = self.session_cart
            self.session.modified = True
        except Exception as e:
            # Gestion des erreurs de sauvegarde de la session
            logger.error(f"Erreur lors de la sauvegarde du panier en session: {e}")
            return redirect("/")

    def clear_session(self) -> None:
        """
        @why: Vider le panier en session.
        @how: Réinitialiser le panier et sauvegarder l'état vide en session.
        """
        try:
            self.session_cart = {}
            self.save_session()
        except Exception as e:
            # Gestion des erreurs de réinitialisation du panier de session
            logger.error(f"Erreur lors du vidage du panier en session: {e}")
            return redirect("/")

    def __iter__(self) -> Generator:
        """
        @why: Itérer sur les articles du panier pour les afficher dans un template ou une API.
        @how: Si le panier est en base de données, on génère les items de la DB. Sinon, on prend ceux de la session.
        """
        try:
            if self.db_cart:
                # Itération sur les articles dans la base de données
                yield from (
                    {
                        "product": item.product,
                        "quantity": item.quantity,
                        "price": item.price,
                        "total_price": item.get_total_price(),
                    }
                    for item in self.db_cart.items.select_related("product").all()
                )
            else:
                # Itération sur les articles dans la session
                products_in_session = {str(product.id): product for product in StoreProduct.objects.filter(id__in=self.session_cart.keys())}
                for product_id, item in self.session_cart.items():
                    if product_id in products_in_session:
                        yield {
                            "product": products_in_session[product_id],
                            "quantity": item["quantity"],
                            "price": Decimal(item["price"]),
                            "total_price": Decimal(item["price"]) * item["quantity"],
                        }
        except Exception as e:
            # Gestion des erreurs d'itération
            logger.error(f"Erreur lors de l'itération des articles du panier: {e}")
            return redirect("/")

    def __len__(self) -> int:
        """
        @why: Retourner le nombre total d'articles dans le panier.
        @how: Si le panier est en base de données, on agrège la quantité des articles. Sinon, on somme les quantités de la session.
        """
        try:
            return (
                self.db_cart.items.aggregate(total=Sum("quantity"))["total"]
                if self.db_cart
                else sum(item["quantity"] for item in self.session_cart.values())
            ) or 0
        except Exception as e:
            # Gestion des erreurs de calcul du nombre d'articles
            logger.error(f"Erreur lors du calcul du nombre total d'articles: {e}")
            return redirect("/")

    def get_cart_subtotal(self) -> Decimal:
        """
        @why: Calculer le sous-total du panier.
        @how: Si le panier est en base de données, on agrège les prix des articles. Sinon, on calcule le sous-total à partir de la session.
        """
        try:
            if self.db_cart:
                subtotal = self.db_cart.items.aggregate(
                    total=Sum(F("price") * F("quantity"))
                )["total"] or Decimal("0.00")
                return subtotal.quantize(Decimal("0.01"))
            else:
                return sum(
                    Decimal(item["price"]) * item["quantity"]
                    for item in self.session_cart.values()
                ).quantize(Decimal("0.01"))
        except Exception as e:
            # Gestion des erreurs de calcul du sous-total
            logger.error(f"Erreur lors du calcul du sous-total: {e}")
            return redirect("/")

    def get_cart_total(self) -> Decimal:
        """
        @why: Calculer le total du panier (identique au sous-total dans ce cas).
        @how: Retourne le résultat de get_cart_subtotal().
        """
        return self.get_cart_subtotal()

    def get_items(self) -> list[dict]:
        """
        @why: Retourner la liste des articles du panier sous forme de dictionnaire.
        @how: Utilise __iter__() pour générer les items du panier et les retourne sous forme de liste.
        """
        return list(self.__iter__())
