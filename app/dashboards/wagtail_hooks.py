# app/dashboard/wagtail_hooks.py
from wagtail import hooks
from wagtail.admin.menu import MenuItem
from django.urls import reverse

@hooks.register("register_admin_menu_item")
def register_sidebar_admin_menu():
    return MenuItem(
        "Sidebar",
        reverse("wagtailsnippets_dashboards_sidebarmenu:list"),
        classname="icon icon-folder-open-inverse",
        order=1000,
    )
