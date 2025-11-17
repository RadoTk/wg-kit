from django.urls import reverse
from wagtail import hooks
from wagtail.admin.menu import MenuItem
from wagtail.models import Page

from .models import ConfessionPage, ConfessionPageIndex


@hooks.register('register_admin_menu_item')
def register_confession_pages_menu_item():
    page = ConfessionPageIndex.objects.live().first()
    if page:
        url = reverse('wagtailadmin_explore', args=[page.id])
    else:
        url = reverse('wagtailadmin_explore', args=[Page.get_first_root_node().id])
    return MenuItem('Confessions', url, icon_name='doc-full-inverse')