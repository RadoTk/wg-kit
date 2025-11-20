from django.db import models
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel

class DashboardPage(Page):
    template = 'dashboard/dashboard_page.html'
    
    banner_text = models.CharField(
        max_length=255, 
        default="OFFRE ABONNEMENT : 20% à vie sur tous les produits"
    )
    
    content_panels = Page.content_panels + [
        FieldPanel('banner_text'),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        
        active_section = request.GET.get('section', 'animaux')
        
        sidebar_menu = [
            { 
                'name': 'Mon espace',
                'slug': 'compte',
                'icon': '',
                'url': f'{self.url}?section=compte'
            },
            {
                'name': 'Mes Animaux',
                'slug': 'animaux',
                'icon': '🐕',
                'url': f'{self.url}?section=animaux'
            },
            {
                'name': 'Mes Commandes', 
                'slug': 'commandes',
                'icon': '📦',
                'url': f'{self.url}?section=commandes'
            },
            {
                'name': 'Abonnements',
                'slug': 'abonnements', 
                'icon': '🔔',
                'url': f'{self.url}?section=abonnements'
            },
            {
                'name': 'Mes Avis',
                'slug': 'avis',
                'icon': '⭐',
                'url': f'{self.url}?section=avis'
            },
            {
                'name': 'Paramètres',
                'slug': 'parametres',
                'icon': '⚙️',
                'url': f'{self.url}?section=parametres'
            },
        ]
        
        context.update({
            'sidebar_menu': sidebar_menu,
            'active_section': active_section,
        })
        
        return context