from django.urls import path, reverse
from wagtail.admin.menu import Menu, MenuItem, SubmenuMenuItem
from wagtail.admin.menu import MenuItem
from wagtail import hooks

from .views import index, month, AgendaViewSet


# @hooks.register('register_admin_urls')
# def register_agenda_url():
#     return [
#         path('agenda/', index, name='agenda'),
#         path('agenda/month/', month, name='agenda-month'),
#     ]

# @hooks.register('register_admin_menu_item')
# def register_agenda_menu_item():
#     submenu = Menu(items=[
#         MenuItem('Agenda', reverse('agenda'), icon_name='date'),
#         MenuItem('Current month', reverse('agenda-month'), icon_name='date'),
#     ])

#     return SubmenuMenuItem('Agenda', submenu, icon_name='date')

# @hooks.register("register_admin_viewset")
# def register_viewset():
#     return AgendaViewSet()
