from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from wagtail.models import Page
from .models import DashboardPage


@login_required(login_url='users/login/')
def dashboard_section(request, page_id=None):
    """Vue sécurisée : accès uniquement aux utilisateurs connectés"""

    # Récupérer la page dashboard
    if page_id:
        page = Page.objects.get(id=page_id).specific
    else:
        page = DashboardPage.objects.live().first()

    # Déterminer la section active
    active_section = request.GET.get('section', 'compte')
    is_partial = request.GET.get('partial') == '1'

    # Contexte
    context = page.get_context(request)
    context['active_section'] = active_section

    # 🔒 Protection partial HTMX
    if is_partial:
        template_name = f"dashboard/partials/{active_section}.html"
        return render(request, template_name, context)

    # Page complète
    return render(request, "dashboard/dashboard_page.html", context)
