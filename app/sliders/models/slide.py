from django.db import models
from wagtail.fields import RichTextField
from wagtail.images.models import Image
from wagtail.admin.panels import FieldPanel, MultiFieldPanel

class Slide(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    description = RichTextField(blank=True)
    background_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+"
    )
    right_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+"
    )
    button_text = models.CharField(max_length=50, blank=True, null=True)
    button_url = models.URLField(blank=True, null=True)

    panels = [
        FieldPanel("title"),
        FieldPanel("subtitle"),
        FieldPanel("description"),
        MultiFieldPanel([
            FieldPanel("background_image"),
            FieldPanel("right_image"),
        ], heading="Images"),
        MultiFieldPanel([
            FieldPanel("button_text"),
            FieldPanel("button_url"),
        ], heading="Bouton"),
    ]

    class Meta:
        verbose_name = "Slide"
        verbose_name_plural = "Slides"

    def __str__(self):
        return self.title
