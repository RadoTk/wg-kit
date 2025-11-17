from django.test import TestCase


class StyleGuideTestCase(TestCase):
    def test_style_guide(self):
        response = self.client.get("/style-guide/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Style Guide")
        self.assertTemplateUsed(response, "style_guide/style_guide.html")
