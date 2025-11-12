from wagtail.contrib.settings.models import BaseGenericSetting, BaseSiteSetting, register_setting
from wagtail.admin.panels import FieldPanel
from django.db import models
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import (
    FieldPanel,
    MultiFieldPanel,
)
from wagtail.models import PreviewableMixin


@register_setting(icon="cog")
class GenericSettings(ClusterableModel, PreviewableMixin, BaseGenericSetting):
    mastodon_url = models.URLField(verbose_name="Mastodon URL", blank=True)
    github_url = models.URLField(verbose_name="GitHub URL", blank=True)
    organisation_url = models.URLField(verbose_name="Organisation URL", blank=True)

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("github_url"),
                FieldPanel("mastodon_url"),
                FieldPanel("organisation_url"),
            ],
            "Social settings",
        )
    ]

    def get_preview_template(self, request, mode_name):
        return "base.html"


@register_setting(icon="site")
class SiteSettings(BaseSiteSetting):
    title_suffix = models.CharField(
        verbose_name="Title suffix",
        max_length=255,
        help_text="The suffix for the title meta tag e.g. ' | The Wagtail Bakery'",
        default="The Wagtail Bakery",
    )

    panels = [
        FieldPanel("title_suffix"),
    ]
