from django.db import models
from wagtail.admin.panels import FieldPanel, InlinePanel
from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey
from wagtail.models import Orderable
from wagtail.snippets.models import register_snippet


STATUS_CHOICES = [
    ("available", "Disponible"),
    ("coming_soon", "Bientôt"),
]


class SidebarMenuItem(Orderable):
    menu = ParentalKey(
        "SidebarMenu",
        on_delete=models.CASCADE,
        related_name="items",
        null=True,
        blank=True
    )
    menu_name = models.CharField(max_length=255)
    url_name = models.CharField(max_length=255, help_text="Nom de l'URL Django")
    icon_class = models.CharField(max_length=100, blank=True, help_text="Classe CSS pour l'icône")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="available")
    is_active = models.BooleanField(default=True)

    panels = [
        FieldPanel("menu_name"),
        FieldPanel("url_name"),
        FieldPanel("icon_class"),
        FieldPanel("status"),
        FieldPanel("is_active"),
    ]

    def __str__(self):
        return self.menu_name


@register_snippet
class SidebarMenu(ClusterableModel):
    title = models.CharField(max_length=255, default="Sidebar Menu")

    panels = [
        FieldPanel("title"),
        InlinePanel("items", label="Items du menu")
    ]

    def __str__(self):
        return self.title
