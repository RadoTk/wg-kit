from django.db import models
from django.conf import settings
from django.utils import timezone
from wagtail.snippets.models import register_snippet
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.images.models import Image
from wagtail.models import Page, Orderable
from wagtail.search import index
from modelcluster.fields import ParentalKey
from django.contrib.auth import get_user_model


User = get_user_model()


class ConfessionTag(models.Model):
    """
    Confession tagging system - can be implemented as Django model or Wagtail Snippet for marketing management
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Confession Tag"
        verbose_name_plural = "Confession Tags"

    def __str__(self):
        return self.name


@register_snippet
class ConfessionCategory(models.Model):
    """
    Confession category as Wagtail Snippet for easier management
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    panels = [
        FieldPanel('name'),
        FieldPanel('description'),
    ]

    class Meta:
        verbose_name = "Confession Category"
        verbose_name_plural = "Confession Categories"

    def __str__(self):
        return self.name


class Confession(models.Model):
    """
    Core confession model based on the Posts application documentation
    """
    TONE_CHOICES = [
        ('ironique', 'Ironique'),
        ('rage', 'Rage'),
        ('desabuse', 'Désabusé'),
        ('triste', 'Triste'),
        ('neutre', 'Neutre'),
        ('joyeux', 'Joyeux'),
        ('courageux', 'Courageux'),
    ]

    # Core fields
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Nullable ForeignKey to User (null for anonymous confessions)"
    )
    pseudo = models.CharField(
        max_length=100,
        blank=True,
        help_text="Auto-generated pseudonym for anonymous content"
    )
    text = models.TextField(help_text="Main text content of the confession")

    # Classification
    tone = models.CharField(
        max_length=20,
        choices=TONE_CHOICES,
        default='neutre',
        help_text="Tone classification for content (ironique, rage, desabusé, etc.)"
    )

    # Relationships
    tags = models.ManyToManyField(ConfessionTag, blank=True)
    category = models.ForeignKey(
        ConfessionCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Visibility and targeting
    is_public = models.BooleanField(default=True, help_text="Boolean indicating if displayed on public feed")
    is_internal = models.BooleanField(default=False, help_text="Boolean indicating company-targeted content")

    # Generated content
    sarcasm_score = models.FloatField(
        null=True,
        blank=True,
        help_text="Float computed by AI for sarcasm detection"
    )
    generated_title = models.CharField(
        max_length=255,
        blank=True,
        help_text="AI-generated title string"
    )
    generated_image = models.ForeignKey(
        Image,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Nullable ForeignKey to Wagtail Image for AI-generated images"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Confession"
        verbose_name_plural = "Confessions"
        ordering = ['-created_at']

    def __str__(self):
        title = self.generated_title or self.text[:50] + "..." if len(self.text) > 50 else self.text
        return f"{title} - {self.pseudo or 'Anonymous'}"

    def save(self, *args, **kwargs):
        # Auto-generate pseudonym if none provided and anonymous
        if not self.pseudo and not self.author_id:
            if not self.id:  # Only for new instances
                from django.utils.text import slugify
                import random
                import string
                random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
                self.pseudo = f"Anonyme_{random_suffix}"
        super().save(*args, **kwargs)


class ConfessionPage(Page):
    """
    Wagtail Page to display confessions
    Since confessions are Django models but need to be displayed via Wagtail,
    this creates a page that can serve as a container for confessions
    """
    intro = RichTextField(blank=True, help_text="Introduction text for the confession page")
    is_public_feed = models.BooleanField(default=True, help_text="Whether this page shows public confessions")

    # If we need to link to a specific category
    category = models.ForeignKey(
        ConfessionCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Filter confessions by category"
    )

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('is_public_feed'),
        FieldPanel('category'),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        # Get confessions based on the page settings
        confessions = Confession.objects.all()
        if self.is_public_feed:
            confessions = confessions.filter(is_public=True)
        if self.category:
            confessions = confessions.filter(category=self.category)
        context['confessions'] = confessions.order_by('-created_at')
        return context


class ConfessionPageIndex(Page):
    intro = RichTextField(blank=True)
    is_public_feed = models.BooleanField(default=True)

    parent_page_types = ["home.HomePage"]
    subpage_types = ["confession.ConfessionPage"]

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('is_public_feed'),
    ]

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        confessions = Confession.objects.all()
        if self.is_public_feed:
            confessions = confessions.filter(is_public=True)
        category_id = request.GET.get('category')
        tone = request.GET.get('tone')
        tag = request.GET.get('tag')
        if category_id:
            confessions = confessions.filter(category_id=category_id)
        if tone:
            confessions = confessions.filter(tone=tone)
        if tag:
            confessions = confessions.filter(tags__name=tag)
        context['confessions'] = confessions.order_by('-created_at')
        return context
