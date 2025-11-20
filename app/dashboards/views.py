from django.shortcuts import render
from .models import SidebarMenuItem


def user_dashboard(request):
    menus = SidebarMenuItem.objects.filter(is_active=True)

    return render(request, "dashboard/user_dashboard.html", {
        "menus": menus
    })
