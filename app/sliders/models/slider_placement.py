from django.db import models
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet

from rootapp.base.models import Slider 



class SliderPlacement(models.Model):
    """Lie un Slider à une Page et une position (ex: 'header', 'testimonials')."""

    POSITION_CHOICES = [
        ("header", "Header"),
        ("testimonials", "Testimonials"),
        ("gallery", "Gallery"),
        ("footer", "Footer"),
    ]

    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name="slider_placements",
        help_text="Page sur laquelle ce slider sera affiché.",
    )
    slider = models.ForeignKey(
        Slider,
        on_delete=models.CASCADE,
        related_name="placements",
        help_text="Le slider à afficher sur cette page.",
    )
    position = models.CharField(
        max_length=50,
        choices=POSITION_CHOICES,
        help_text="Section où afficher ce slider (ex: header, testimonials...).",
    )

    panels = [
        FieldPanel("page"),
        FieldPanel("slider"),
        FieldPanel("position"),
    ]

    class Meta:
        verbose_name = "Slider Placement"
        verbose_name_plural = "Slider Placements"

    def __str__(self):
        return f"{self.page.title} → {self.slider.name} ({self.position})"
