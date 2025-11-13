from django.db import models

from django.http import HttpRequest

from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.fields import RichTextField
from wagtail.models import Page

from app.cart.forms import CartAddProductForm


from app.page_links.models import GenericPageLink
from django.contrib.contenttypes.fields import GenericRelation


class StoreIndexPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    parent_page_types = ["home.HomePage"]
    subpage_types: list[str] = [
        "store.StoreProductIndexPage",
    ]
    max_count = 1

    def get_context(self, request, *args, **kwargs) -> dict:
        context = super().get_context(request)
        context["products"] = StoreProduct.objects.all().order_by("-is_featured", "title")
        context["cart_add_product_form"] = CartAddProductForm()
        return context
    


class StoreProductIndexPage(Page):
    max_count = 1
    parent_page_types = [
        "store.StoreIndexPage",
    ]
    subpage_types = ["store.StoreProduct"]

    def get_context(self, request):
        context = super().get_context(request)
        context["products"] = self.get_children().type(StoreProduct).live()
        return context

class StoreProduct(Page):
    image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    description = RichTextField(blank=True)
    price_usd = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True, verbose_name="Disponible à la vente")
    is_featured = models.BooleanField(default=False)

    parent_page_types = ["store.StoreProductIndexPage"]
    subpage_types = []

    content_panels = Page.content_panels + [
        FieldPanel("description", classname="full"),
        MultiFieldPanel([
            FieldPanel("price_usd"),
            FieldPanel("is_available"),
            FieldPanel("is_featured"),
        ], heading="Informations produit"),
        FieldPanel("image"),
        InlinePanel("linked_objects", label="Liens vers d'autres pages"),
    ]



    def get_context(
        self,
        request: HttpRequest,
        *args: tuple,
        **kwargs: dict,
    ) -> dict:
        context = super().get_context(request)

        context["cart_add_product_form"] = CartAddProductForm()

        return context

    @property
    def price(self) -> str:
        """Alias of price_usd for backwards compatibility."""
        return self.price_usd

