from django import template
from django.urls import reverse
from wagtail.models import Page, Site

register = template.Library()

@register.simple_tag
def get_dashboard_url():
    """
    Retourne l'URL complète du dashboard
    """
    try:
        from app.dashboard.models import DashboardPage
        
        # Prendre la première DashboardPage publiée
        dashboard_page = DashboardPage.objects.live().first()
        
        if dashboard_page:
            # Méthode 1: Utiliser get_full_url() qui inclut le chemin complet
            full_url = dashboard_page.get_full_url()
            if full_url:
                return full_url
            
            # Méthode 2: Construire l'URL manuellement avec le site
            site = Site.find_for_request(dashboard_page)
            if site:
                root_url = site.root_url
                page_url = dashboard_page.get_url()
                return root_url + page_url
            
            # Méthode 3: URL relative
            return dashboard_page.get_url()
                
    except Exception as e:
        print(f"DEBUG Error: {e}")
        pass
    
    # Fallback hardcodé avec le bon chemin
    return '/dogs-daisies/dashboard/'