from django.shortcuts import get_object_or_404, redirect
from .models import GenericPageLink
from django.contrib.contenttypes.models import ContentType
from app.store.models import StoreProduct

def redirect_to_link(request, source_model, source_id):
    """
    Redirige automatiquement vers la cible du lien associé à un objet source.
    """
    # Récupérer le ContentType correspondant
    content_type = get_object_or_404(ContentType, model=source_model)

    # Chercher le lien
    link = get_object_or_404(GenericPageLink, source_type=content_type, source_id=source_id)

    # Redirection automatique vers la cible
    return redirect(link.target_url)  # <-- ici, target_url et non target_object.url

def store_product_redirect(request, product_id):
    """
    Redirige automatiquement vers la page liée d'un produit Wagtail StoreProduct
    """
    product = get_object_or_404(StoreProduct, id=product_id)
    link = product.linked_objects.first()  # ici linked_objects vient du modèle PageLink
    if link:
        return redirect(link.linked_page.url)
    return redirect(product.url)
