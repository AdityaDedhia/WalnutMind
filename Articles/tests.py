from django.test import TestCase
from . models import Post


class URLTests(TestCase):
    def test_urls(self):
        response = self.client.get('/', {}, True)
        self.assertEqual(response.status_code, 200)
