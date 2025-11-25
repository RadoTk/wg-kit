# dashboard/models.py
from django.db import models
from django.urls import reverse
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel
from app.animals.models import Animal

class DashboardPage(Page):
    template = 'dashboard/dashboard_page.html'
    
    banner_text = models.CharField(
        max_length=255, 
        default="OFFRE ABONNEMENT : 20% à vie sur tous les produits"
    )
    
    content_panels = Page.content_panels + [
        FieldPanel('banner_text'),
    ]

    def get_sidebar_menu(self, request, active_section=None):
        """Génère le menu sidebar"""
        menu_items = [
            {
                'name': 'Mon espace',
                'slug': 'compte',
                'icon': '👤',
                'url': reverse('dashboard:dashboard_section', kwargs={'section_name': 'my_account'}),
                'status': 'disponible'
            },
            {
                'name': 'Mes Animaux',
                'slug': 'animaux', 
                'icon': '🐕',
                'url': reverse('dashboard:dashboard_section', kwargs={'section_name': 'my_animal_list'}),
                'status': 'disponible'
            },
            {
                'name': 'Mes Commandes',
                'slug': 'commandes',
                'icon': '📦', 
                'url': reverse('dashboard:dashboard_section', kwargs={'section_name': 'my_command'}),
                'status': 'disponible'
            },
            {
                'name': 'Abonnements',
                'slug': 'abonnements',
                'icon': '🔔',
                'url': reverse('dashboard:dashboard_section', kwargs={'section_name': 'subscription'}),
                'status': 'disponible'
            },
            {
                'name': 'Mes Avis',
                'slug': 'avis',
                'icon': '⭐',
                'url': reverse('dashboard:dashboard_section', kwargs={'section_name': 'my_opinion'}),
                'status': 'bientôt'
            },
            {
                'name': 'Paramètres',
                'slug': 'parametres',
                'icon': '⚙️',
                'url': reverse('dashboard:dashboard_section', kwargs={'section_name': 'account_parameter'}),
                'status': 'disponible'
            },
        ]
        
        # Marquer l'élément actif
        for item in menu_items:
            item['is_active'] = item['slug'] == active_section
            
        return menu_items

    def get_section_data(self, request, template_section):
        """Récupère les données spécifiques à chaque section"""
        user = request.user
        
        if template_section == 'my_account':
            return {
                'animals_count': Animal.objects.filter(owner=user).count(),
                'orders_count': 3,
                'subscriptions_count': 2
            }
        elif template_section == 'my_animal_list':
            return {
                'animals': Animal.objects.filter(owner=user)
            }
        elif template_section == 'my_command':
            return {
                'orders': [
                    {'order_number': 'CMD-001', 'order_date': '2024-01-15', 'status': 'Livré'},
                    {'order_number': 'CMD-002', 'order_date': '2024-01-20', 'status': 'En cours'},
                ]
            }
        elif template_section == 'subscription':
            return {
                'subscriptions': [
                    {'product_name': 'Croquettes Premium', 'status': 'Actif', 'start_date': '2024-01-01'},
                    {'product_name': 'Soins Vétérinaires', 'status': 'Actif', 'start_date': '2024-01-10'},
                ]
            }
        elif template_section == 'my_opinion':
            return {'reviews': []}
        elif template_section == 'account_parameter':
            return {'user': user}
            
        return {}

    def get_context(self, request, active_section='compte', *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        
        # Mapping sections
        section_to_template_map = {
            'compte': 'my_account',
            'animaux': 'my_animal_list',
            'commandes': 'my_command',
            'abonnements': 'subscription', 
            'avis': 'my_opinion',
            'parametres': 'account_parameter'
        }
        
        template_section = section_to_template_map.get(active_section, 'my_account')
        
        context.update({
            'sidebar_menu': self.get_sidebar_menu(request, active_section),
            'active_section': active_section,
            'template_section': template_section,
        })
        
        # Données spécifiques à la section
        section_data = self.get_section_data(request, template_section)
        context.update(section_data)
        
        return context