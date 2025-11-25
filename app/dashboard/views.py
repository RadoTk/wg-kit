# dashboard/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from wagtail.models import Page
from .models import DashboardPage

@login_required
def dashboard_view(request, section_name=None):
    """
    Vue unique pour gérer le dashboard
    Gère à la fois les requêtes complètes et partielles HTMX
    """
    page = DashboardPage.objects.live().first()
    is_partial = request.headers.get('HX-Request', False)
    
    # Mapping entre URLs et sections
    url_to_section_map = {
        'my_account': 'compte',
        'my_animal_list': 'animaux', 
        'my_command': 'commandes',
        'subscription': 'abonnements',
        'my_opinion': 'avis',
        'account_parameter': 'parametres'
    }
    
    section_to_template_map = {
        'compte': 'my_account',
        'animaux': 'my_animal_list',
        'commandes': 'my_command', 
        'abonnements': 'subscription',
        'avis': 'my_opinion',
        'parametres': 'account_parameter'
    }
    
    # Déterminer la section active
    if section_name:
        # Depuis l'URL (/dashboard/section/my_animal_list/)
        active_section = url_to_section_map.get(section_name, 'compte')
    else:
        # Depuis les paramètres GET (/dashboard/?section=animaux)
        active_section = request.GET.get('section', 'compte')
    
    # Template section correspondante
    template_section = section_to_template_map.get(active_section, 'my_account')
    
    # Contexte
    context = page.get_context(request, active_section=active_section)
    context['template_section'] = template_section
    
    # Réponse selon le type de requête
    if is_partial:
        # Requête HTMX - retourner seulement le partial
        template_name = f"dashboard/partials/{template_section}.html"
        return render(request, template_name, context)
    else:
        # Requête normale - retourner la page complète
        return render(request, "dashboard/dashboard_page.html", context)