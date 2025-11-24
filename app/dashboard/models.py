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
        active_section = request.GET.get('section', 'compte')
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
                'url': f'{page_url}?section=compte',
                'status': 'disponible'
            },
            {
                'name': 'Mes Animaux',
                'slug': 'animaux',
                'icon': '🐕',
                'url': f'{page_url}?section=animaux',
                'status': 'disponible'
            },
            {
                'name': 'Mes Commandes', 
                'slug': 'commandes',
                'icon': '📦',
                'url': f'{page_url}?section=commandes',
                'status': 'disponible'
            },
            {
                'name': 'Abonnements',
                'slug': 'abonnements', 
                'icon': '🔔',
                'url': f'{page_url}?section=abonnements',
                'status': 'disponible'
            },
            {
                'name': 'Mes Avis',
                'slug': 'avis',
                'icon': '⭐',
                'url': f'{page_url}?section=avis',
                'status': 'bientôt'
            },
            {
                'name': 'Paramètres',
                'slug': 'parametres',
                'icon': '⚙️',
                'url': f'{page_url}?section=parametres',
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
        if active_section == 'compte':
            user = request.user

            context.update({
                'animals_count': Animal.objects.filter(owner=user).count(),
                'orders_count': 3,
                'subscriptions_count': 2
            })
        elif active_section == 'animaux':
            user = request.user
            context['animals'] = [Animal.objects.filter(owner=user)]
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
        
        return context