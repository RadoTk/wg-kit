from django.db import models
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

    def get_template(self, request, *args, **kwargs):
        """Détermine le template en fonction de la section active"""
        active_section = request.GET.get('section', 'my_account')
        is_partial = request.GET.get('partial') == '1'
        
        if is_partial:
            return f'dashboard/partials/{active_section}.html'
        return 'dashboard/dashboard_page.html'

    def get_sidebar_menu(self, request):
        page_url = self.get_url(request) if request else self.url
        
        return [
            {
                'name': 'Mon espace',
                'slug': 'compte',
                'icon': '👤',
                'url': f'{page_url}?section=my_account',
                'status': 'disponible'
            },
            {
                'name': 'Mes Animaux',
                'slug': 'animaux',
                'icon': '🐕',
                'url': f'{page_url}?section=my_animal_list',
                'status': 'disponible'
            },
            {
                'name': 'Mes Commandes', 
                'slug': 'commandes',
                'icon': '📦',
                'url': f'{page_url}?section=my_command',
                'status': 'disponible'
            },
            {
                'name': 'Abonnements',
                'slug': 'abonnements', 
                'icon': '🔔',
                'url': f'{page_url}?section=subscription',
                'status': 'disponible'
            },
            {
                'name': 'Mes Avis',
                'slug': 'avis',
                'icon': '⭐',
                'url': f'{page_url}?section=my_opinion',
                'status': 'bientôt'
            },
            {
                'name': 'Paramètres',
                'slug': 'parametres',
                'icon': '⚙️',
                'url': f'{page_url}?section=account_parameter',
                'status': 'disponible'
            },
        ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        
        active_section = request.GET.get('section', 'compte')
        
        context.update({
            'sidebar_menu': self.get_sidebar_menu(request),
            'active_section': active_section,
        })
        
        # Données de démonstration
        if active_section == 'my_account':
            user = request.user

            context.update({
                'animals_count': Animal.objects.filter(owner=user).count(),
                'orders_count': 3,
                'subscriptions_count': 2
            })

        elif active_section == 'my_animal_list':
            user = request.user
            context['animals'] = Animal.objects.filter(owner=user)
        elif active_section == 'my_command':
            context['orders'] = [
                {'order_number': 'CMD-001', 'order_date': '2024-01-15', 'status': 'Livré'},
                {'order_number': 'CMD-002', 'order_date': '2024-01-20', 'status': 'En cours'},
            ]
        elif active_section == 'subscription':
            context['subscriptions'] = [
                {'product_name': 'Croquettes Premium', 'status': 'Actif', 'start_date': '2024-01-01'},
                {'product_name': 'Soins Vétérinaires', 'status': 'Actif', 'start_date': '2024-01-10'},
            ]
        elif active_section == 'my_opinion':
            context['reviews'] = []
        
        return context