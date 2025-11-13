import logging
from django.shortcuts import redirect, get_object_or_404, render
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.views.decorators.http import require_POST, require_GET

from app.store.models import StoreProduct, StoreIndexPage
from .cart import Cart
from .forms import CartAddProductForm

logger = logging.getLogger(__name__)

def render_cart_summary(request, cart: Cart):
    """
    Génère et retourne le résumé du panier sous forme HTML.

    @param request: L'objet request pour obtenir des informations supplémentaires.
    @param cart: L'objet panier contenant les articles.
    @return: Une réponse HTTP contenant le rendu HTML du résumé du panier.
    """
    try:
        # On récupère la première page d'index de la boutique
        store_index_page = StoreIndexPage.objects.first()
        # On génère le résumé du panier avec les informations nécessaires
        html = render_to_string(
            "cart/_cart_summary.html",
            {"cart": cart, "store_index_page": store_index_page},
            request=request,
        )
        return HttpResponse(html)
    except Exception as e:
        logger.error(f"Erreur lors du rendu du résumé du panier : {e}")
        return HttpResponse("Une erreur est survenue lors du rendu du panier.", status=500)



@require_POST
def cart_add(request, product_id):
    """
    Ajoute un produit au panier.

    @param request: L'objet request contenant les données du formulaire.
    @param product_id: L'ID du produit à ajouter.
    @return: Redirection vers la page de détail du panier ou mise à jour dynamique si c'est une requête HX.
    """
    try:
        cart = Cart(request)  # Initialisation du panier
        product = get_object_or_404(StoreProduct, id=product_id)  # Recherche du produit par ID
        form = CartAddProductForm(request.POST)

        if form.is_valid():
            quantity = form.cleaned_data["quantity"]  # Quantité du produit à ajouter
            cart.add(product, quantity)  # Ajoute le produit au panier

        # Si la requête est HX (requête Ajax), on renvoie un résumé dynamique du panier
        if request.headers.get("Hx-Request"):
            return render_cart_summary(request, cart)

        # Sinon, redirige vers la page de détail du panier
        return redirect("cart:cart_detail")

    except Exception as e:
        logger.error(f"Erreur lors de l'ajout d'un produit au panier: {e}")
        return redirect("cart:cart_detail")  # Redirige pour éviter que l'utilisateur rencontre une page cassée



@require_GET
def cart_remove(request, product_id):
    """
    Supprime un produit du panier.

    @param request: L'objet request.
    @param product_id: L'ID du produit à supprimer.
    @return: Redirection vers la page de détail du panier ou mise à jour dynamique si c'est une requête HX.
    """
    try:
        cart = Cart(request)
        product = get_object_or_404(StoreProduct, id=product_id)  # Recherche du produit à supprimer
        cart.remove(product)  # Supprime le produit du panier

        if request.headers.get("Hx-Request"):
            return render_cart_summary(request, cart)

        return redirect("cart:cart_detail")
    
    except Exception as e:
        logger.error(f"Erreur lors de la suppression du produit {product_id} du panier: {e}")
        return redirect("cart:cart_detail")  # Redirige pour éviter un plantage de la page


@require_POST
def cart_update(request, product_id):
    """
    Met à jour la quantité d'un produit dans le panier.

    @param request: L'objet request contenant les données du formulaire.
    @param product_id: L'ID du produit dont la quantité doit être mise à jour.
    @return: Redirection vers la page de détail du panier ou mise à jour dynamique si c'est une requête HX.
    """
    try:
        cart = Cart(request)
        product = get_object_or_404(StoreProduct, id=product_id)
        form = CartAddProductForm(request.POST)

        if form.is_valid():
            quantity = form.cleaned_data["quantity"]
            if quantity <= 0:
                cart.remove(product)  # Si la quantité est inférieure ou égale à 0, on supprime le produit
            else:
                cart.add(product, quantity, replace_quantity=True)  # Sinon, on met à jour la quantité

        if request.headers.get("Hx-Request"):
            return render_cart_summary(request, cart)

        return redirect("cart:cart_detail")

    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour de la quantité pour le produit {product_id}: {e}")
        return redirect("cart:cart_detail")  # Redirige si une erreur se produit


@require_GET
def show_cart_detail(request):
    """
    Affiche le détail du panier, avec la possibilité de modifier les quantités.

    @param request: L'objet request.
    @return: Affiche la page de détail du panier avec les informations et les formulaires nécessaires.
    """
    try:
        cart = Cart(request)

        # Ajoute le formulaire de mise à jour de la quantité à chaque item du panier
        for item in cart:
            item["update_quantity_form"] = CartAddProductForm(initial={"quantity": item["quantity"]})

        store_index_page = StoreIndexPage.objects.first()
        context = {"cart": cart, "store_index_page": store_index_page}

        return render(request, "cart/cart_detail.html", context)

    except Exception as e:
        logger.error(f"Erreur lors de l'affichage du détail du panier: {e}")
        return HttpResponse("Une erreur est survenue lors de l'affichage du panier.", status=500)
