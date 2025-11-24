from django.db import models
from django.db.models import Q
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page


CATEGORY_CHOICES = (
    ("chien", "Chien"),
    ("chat", "Chat"),
    ("bon_a_savoir", "Bon à savoir"),
    ("guide", "Guide"),
)


class AdviceIndexPage(Page):
    parent_page_types = ["home.HomePage"]
    subpage_types = ["advice.AdvicePage"]

    def get_context(self, request):
        context = super().get_context(request)
        qs = AdvicePage.objects.child_of(self).live()

        category = request.GET.get("category")
        if category in {c[0] for c in CATEGORY_CHOICES}:
            qs = qs.filter(category=category)

        q = request.GET.get("q")
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(excerpt__icontains=q))

        qs = qs.order_by("-date")

        featured = list(qs.filter(is_featured=True)[:3])
        featured_ids = [p.id for p in featured]

        articles = (featured + list(qs.exclude(id__in=featured_ids)))[:4]
        # articles = qs.exclude(id__in=featured_ids)

        context.update({
            "featured": featured,
            "articles": articles,
            "category": category,
            "q": q,
        })
        return context


class AdvicePage(Page):
    parent_page_types = ["advice.AdviceIndexPage"]

    date = models.DateField("Date")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    excerpt = models.CharField(max_length=300, blank=True)
    body = RichTextField(blank=True)
    listing_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    is_featured = models.BooleanField(default=False)

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel("date"),
            FieldPanel("category"),
            FieldPanel("listing_image"),
            FieldPanel("is_featured"),
        ], heading="Listing"),
        FieldPanel("excerpt"),
        FieldPanel("body"),
    ]

# Create your models here.
