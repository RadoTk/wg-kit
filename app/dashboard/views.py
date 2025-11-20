from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard_section(request):
    # Déterminer la section active depuis l'URL
    active_section = request.GET.get('section', 'animaux')
    
    # Menu sidebar avec statuts
    dashboard_url = '/dashboard/'
    sidebar_menu = [
        {
            'name': 'Mes Animaux',
            'slug': 'animaux',
            'icon': '🐕',
            'url': f'{dashboard_url}?section=animaux',
            'status': 'disponible'
        },
        {
            'name': 'Mes Commandes', 
            'slug': 'commandes',
            'icon': '📦',
            'url': f'{dashboard_url}?section=commandes',
            'status': 'disponible'
        },
        {
            'name': 'Abonnements',
            'slug': 'abonnements', 
            'icon': '🔔',
            'url': f'{dashboard_url}?section=abonnements',
            'status': 'disponible'
        },
        {
            'name': 'Mes Avis',
            'slug': 'avis',
            'icon': '⭐',
            'url': f'{dashboard_url}?section=avis',
            'status': 'bientôt'
        },
        {
            'name': 'Paramètres',
            'slug': 'parametres',
            'icon': '⚙️',
            'url': f'{dashboard_url}?section=parametres',
            'status': 'disponible'
        },
    ]
    
    # Simuler des données pour la démonstration
    # Dans la réalité, ces données viendront de vos applications existantes
    context = {
        'sidebar_menu': sidebar_menu,
        'active_section': active_section,
        'user': request.user,
        'page': {
            'banner_text': "OFFRE ABONNEMENT : 20% à vie sur tous les produits",
            'title': 'Mon Espace'
        }
    }
    
    # Ajouter des données de démonstration selon la section
    if active_section == 'animaux':
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
        context['reviews'] = []  # Aucun avis pour l'instant
    elif active_section == 'parametres':
        # Données pour les paramètres
        pass
    
    template_name = f"dashboard/sections/{active_section}.html"
    
    return render(request, template_name, context)