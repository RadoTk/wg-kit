from django.test import TestCase


class SearchTestCase(TestCase):
    def test_search_view(self):
        response = self.client.get("/search/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Search")
        self.assertTemplateUsed(response, "search/search.html")

    def test_seach_no_results(self):
        response = self.client.get("/search/?query=empty")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No results found")
        self.assertTemplateUsed(response, "search/search.html")

    def test_search_empty_query(self):
        response = self.client.get("/search/?query=")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "No results found")
        self.assertTemplateUsed(response, "search/search.html")
