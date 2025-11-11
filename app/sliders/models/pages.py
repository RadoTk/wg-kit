from django.db import models
from wagtail.models import (
    Collection,
    Page,
)
from wagtail.admin.panels import (
    FieldPanel,
    HelpPanel,
    MultiFieldPanel,
)
from wagtail.api import APIField
from wagtail.fields import RichTextField, StreamField
from rootapp.base.blocks import BaseStreamBlock





class StandardPage(Page):
    """
    A generic content page. On this demo site we use it for an about page but
    it could be used for any type of page content that only needs a title,
    image, introduction and body field
    """

    introduction = models.TextField(help_text="Text to describe the page", blank=True)
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Landscape mode only; horizontal width between 1000px and 3000px.",
    )
    body = StreamField(
        BaseStreamBlock(), verbose_name="Page body", blank=True, use_json_field=True
    )
    content_panels = Page.content_panels + [
        FieldPanel("introduction"),
        FieldPanel("body"),
        FieldPanel("image"),
    ]

    api_fields = [
        APIField("introduction"),
        APIField("image"),
        APIField("body"),
    ]


class HomePage(Page):
    """
    The Home Page. This looks slightly more complicated than it is. You can
    see if you visit your site and edit the homepage that it is split between
    a:
    - Hero area
    - Body area
    - A promotional area
    - Moveable featured site sections
    """

    # Hero section of HomePage
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Homepage image",
    )
    hero_text = models.CharField(
        max_length=255, help_text="Write an introduction for the bakery"
    )
    hero_cta = models.CharField(
        verbose_name="Hero CTA",
        max_length=255,
        help_text="Text to display on Call to Action",
    )
    hero_cta_link = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Hero CTA link",
        help_text="Choose a page to link to for the Call to Action",
    )

    # Body section of the HomePage
    body = StreamField(
        BaseStreamBlock(),
        verbose_name="Home content block",
        blank=True,
        use_json_field=True,
    )

    slider = models.ForeignKey(
        "base.Slider",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Choisissez le slider à afficher sur cette page"
    )

    # Promo section of the HomePage
    promo_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Promo image",
    )
    promo_title = models.CharField(
        blank=True, max_length=255, help_text="Title to display above the promo copy"
    )
    promo_text = RichTextField(
        null=True, blank=True, max_length=1000, help_text="Write some promotional copy"
    )

    # Featured sections on the HomePage
    # You will see on templates/base/home_page.html that these are treated
    # in different ways, and displayed in different areas of the page.
    # Each list their children items that we access via the children function
    # that we define on the individual Page models e.g. BlogIndexPage
    featured_section_1_title = models.CharField(
        blank=True,
        max_length=255,
        help_text="Title to display above the featured section 1",
    )
    featured_section_1 = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="First featured section for the homepage. Will display up to "
        "three child items.",
        verbose_name="Featured section 1",
    )

    featured_section_2_title = models.CharField(
        blank=True,
        max_length=255,
        help_text="Title to display above the featured section 2",
    )
    featured_section_2 = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Second featured section for the homepage. Will display up to "
        "three child items.",
        verbose_name="Featured section 2",
    )

    featured_section_3_title = models.CharField(
        blank=True,
        max_length=255,
        help_text="Title to display above the featured section 3",
    )
    featured_section_3 = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Third featured section for the homepage. Will display up to "
        "six child items.",
        verbose_name="Featured section 3",
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("image"),
                FieldPanel("hero_text"),
                MultiFieldPanel(
                    [
                        FieldPanel("hero_cta"),
                        FieldPanel("hero_cta_link"),
                    ]
                ),
            ],
            heading="Hero section",
        ),
        HelpPanel("This is a help panel"),
        FieldPanel("slider"),
        MultiFieldPanel(
            [
                FieldPanel("promo_image"),
                FieldPanel("promo_title"),
                FieldPanel("promo_text"),
            ],
            heading="Promo section",
            help_text="This is just a help text",
        ),
        FieldPanel("body"),
        MultiFieldPanel(
            [
                MultiFieldPanel(
                    [
                        FieldPanel("featured_section_1_title"),
                        FieldPanel("featured_section_1"),
                    ]
                ),
                MultiFieldPanel(
                    [
                        FieldPanel("featured_section_2_title"),
                        FieldPanel("featured_section_2"),
                    ]
                ),
                MultiFieldPanel(
                    [
                        FieldPanel("featured_section_3_title"),
                        FieldPanel("featured_section_3"),
                    ]
                ),
            ],
            heading="Featured homepage sections",
        ),
    ]

    api_fields = [
        APIField("image"),
        APIField("hero_text"),
        APIField("hero_cta"),
        APIField("hero_cta_link"),
        APIField("body"),
        APIField("promo_image"),
        APIField("promo_title"),
        APIField("promo_text"),
        APIField("featured_section_1_title"),
        APIField("featured_section_1"),
        APIField("featured_section_2_title"),
        APIField("featured_section_2"),
        APIField("featured_section_3_title"),
        APIField("featured_section_3"),
    ]

    def __str__(self):
        return self.title
    
    # def get_template(self, request, *args, **kwargs):
    #     return "orfarm/index-6.html"


class GalleryPage(Page):
    """
    This is a page to list locations from the selected Collection. We use a Q
    object to list any Collection created (/admin/collections/) even if they
    contain no items. In this demo we use it for a GalleryPage,
    and is intended to show the extensibility of this aspect of Wagtail
    """

    introduction = models.TextField(help_text="Text to describe the page", blank=True)
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Landscape mode only; horizontal width between 1000px and 3000px.",
    )
    body = StreamField(
        BaseStreamBlock(), verbose_name="Page body", blank=True, use_json_field=True
    )
    collection = models.ForeignKey(
        Collection,
        limit_choices_to=~models.Q(name__in=["Root"]),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Select the image collection for this gallery.",
    )

    content_panels = Page.content_panels + [
        FieldPanel("introduction"),
        FieldPanel("body"),
        FieldPanel("image"),
        FieldPanel("collection"),
    ]

    # Defining what content type can sit under the parent. Since it's a blank
    # array no subpage can be added
    subpage_types = []

    api_fields = [
        APIField("introduction"),
        APIField("image"),
        APIField("body"),
        APIField("collection"),
    ]

class WishlistPage(Page):
    def get_context(self, request, *args, **kwargs) -> dict:
        context = super().get_context(request)
        context["products"] = "StoreProduct.objects.all().order_by"
        context["cart_add_product_form"] = "CartAddProductForm()"
        return context




class SimpleContentPage(Page):
    """
    A simple content page with a small image, a large title, a subtitle, and a paragraph.
    """

    # Small image field (for a small thumbnail or icon)
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="A small image to represent the page.",
    )

    # Large title (main heading)
    large_title = models.CharField(max_length=255, help_text="Main title for the page")

    # Subtitle (smaller title)
    subtitle = models.CharField(max_length=255, help_text="A subtitle or secondary title")

    # Paragraph description
    description = models.TextField(help_text="A description or content for the page", blank=True)

    # Adding content panels with FieldPanel for the image (since ImageChooserPanel doesn't work)
    content_panels = Page.content_panels + [
        FieldPanel("image"),  # Here we use FieldPanel instead of ImageChooserPanel
        FieldPanel("large_title"),
        FieldPanel("subtitle"),
        FieldPanel("description"),
    ]

    api_fields = [
        APIField("image"),
        APIField("large_title"),
        APIField("subtitle"),
        APIField("description"),
    ]

    def __str__(self):
        return self.large_title



