from django.test import TestCase, override_settings
from django.urls import reverse
from wagtail.models import Page, Site
from app.home.models import HomePage
from app.confession.models import Confession, ConfessionPageIndex


@override_settings(STORAGES={
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}
})
class ConfessionPageIndexTests(TestCase):
    def setUp(self):
        self.home = HomePage.objects.first()
        if not self.home:
            root = Page.get_first_root_node()
            self.home = HomePage(title="Home")
            root.add_child(instance=self.home)
            self.home.save_revision().publish()

        self.index = ConfessionPageIndex(title="Confessions")
        self.home.add_child(instance=self.index)
        self.index.save_revision().publish()

        Confession.objects.create(text="Public confession", is_public=True)
        Confession.objects.create(text="Private confession", is_public=False)

    def test_index_page_serves_public_confessions(self):
        response = self.client.get(self.index.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Public confession")
        self.assertNotContains(response, "Private confession")
