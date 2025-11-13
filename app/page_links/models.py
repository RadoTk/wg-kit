from django.db import models
from wagtail.models import Orderable
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel

class GenericPageLink(Orderable):
    page = ParentalKey(
        "store.StoreProduct",
        on_delete=models.CASCADE,
        related_name="linked_objects"
    )
    title = models.CharField(max_length=255)
    url = models.URLField("Lien externe", blank=True, null=True)

    panels = [
        FieldPanel("title"),
        FieldPanel("url"),
    ]

    def __str__(self):
        return self.title or "Lien sans titre"
