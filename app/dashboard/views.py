from django.shortcuts import render
from django.http import HttpResponse
from wagtail.models import Page
from .models import DashboardPage

def dashboard_section(request, page_id=None):
    """Vue qui gère à la fois le chargement complet et les partials HTMX"""
    # Récupérer la page dashboard
    if page_id:
        page = Page.objects.get(id=page_id).specific
    else:
        page = DashboardPage.objects.live().first()
    
    # Déterminer la section active
    active_section = request.GET.get('section', 'compte')
    is_partial = request.GET.get('partial') == '1'
    
    # Préparer le contexte
    context = page.get_context(request)
    context['active_section'] = active_section
    
    # Ajouter les données spécifiques à la section
    _add_section_data(context, active_section)
    
    # Si c'est une requête HTMX (partial), renvoyer seulement le template partiel
    if is_partial:
        template_name = f"dashboard/partials/{active_section}.html"
        return render(request, template_name, context)
    
    # CORRECTION : Utiliser render() au lieu de page.serve()
    # pour éviter la duplication des headers/footers
    template_name = "dashboard/dashboard_page.html"
    return render(request, template_name, context)

def _add_section_data(context, active_section):
    """Ajoute les données spécifiques à chaque section"""
    if active_section == 'compte':
        context.update({
            'animals_count': 2,
            'orders_count': 3,
            'subscriptions_count': 2
        })
    elif active_section == 'animaux':
        context['animals'] = [
            {'name': 'Rex', 'animal_type': 'dog', 'get_animal_type_display': 'Chien'},
            {'name': 'Misty', 'animal_type': 'cat', 'get_animal_type_display': 'Chat'},
        ]
    elif active_section == 'commandes':
        context['orders'] = [
            {'order_number': 'CMD-001', 'order_date': '2024-01-15', 'status': 'Livré'},
            {'order_number': 'CMD-002', 'order_date': '2024-01-20', 'status': 'En cours'},
        ]
    elif active_section == 'abonnements':
        context['subscriptions'] = [
            {'product_name': 'Croquettes Premium', 'status': 'Actif', 'start_date': '2024-01-01'},
            {'product_name': 'Soins Vétérinaires', 'status': 'Actif', 'start_date': '2024-01-10'},
        ]
    elif active_section == 'avis':
        context['reviews'] = []