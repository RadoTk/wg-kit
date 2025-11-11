from django.db import models
from wagtail.snippets.models import register_snippet
from wagtail.admin.panels import FieldPanel, InlinePanel
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.models import Orderable


class Slider(ClusterableModel):
    """Un groupe de slides, ex: 'Slider Page d'accueil'"""
    name = models.CharField(max_length=255, help_text="Nom interne du slider (pour le retrouver facilement)")
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True, null=True, help_text="Description interne (facultative)")

    panels = [
        FieldPanel("name"),
        FieldPanel("description"),
        InlinePanel("slide_items", label="Slides"),
    ]

    class Meta:
        verbose_name = "Slider"
        verbose_name_plural = "Sliders"

    def __str__(self):
        return self.name


class SliderItem(Orderable):
    """Relie un slide à un slider (avec ordre configurable)"""
    slider = ParentalKey(Slider, related_name="slide_items", on_delete=models.CASCADE)
    slide = models.ForeignKey("base.Slide", on_delete=models.CASCADE, related_name="+")
    
    panels = [
        FieldPanel("slide"),
    ]

    def __str__(self):
        return f"{self.slider.name} → {self.slide.title}"
