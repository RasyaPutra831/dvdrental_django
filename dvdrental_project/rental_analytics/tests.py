from django.test import SimpleTestCase
from django.urls import resolve, reverse


class UrlRoutingTests(SimpleTestCase):
    """Check that the main analytics routes resolve to the expected views."""

    def test_movie_page_route(self):
        self.assertEqual(resolve("/analytics/movie/").url_name, "movie_page")

    def test_predict_movie_route(self):
        self.assertEqual(reverse("predict_movie"), "/analytics/predict-movie/")

    def test_home_route(self):
        self.assertEqual(resolve("/").url_name, "home")
