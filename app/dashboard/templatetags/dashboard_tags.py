from django import template
from wagtail.models import Site
from app.dashboard.models import DashboardPage

register = template.Library()

@register.simple_tag(takes_context=True)
def get_dashboard_url(context):
    """
    Retourne l'URL absolue du dashboard pour l'utilisateur connecté.
    """
    request = context.get("request")

    dashboard_page = DashboardPage.objects.live().first()
    if not dashboard_page:
        return "#"

    # Si request est disponible → meilleure méthode
    if request:
        return dashboard_page.get_url(request=request)

    # Sinon → URL absolue Wagtail
    return dashboard_page.get_full_url() or dashboard_page.get_url()
