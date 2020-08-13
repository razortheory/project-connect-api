from django.test import TestCase

from proco.locations.tests.factories import CountryFactory
from proco.utils.tests import TestAPIViewSetMixin


class CountryApiTestCase(TestAPIViewSetMixin, TestCase):
    base_view = 'locations:countries'

    @classmethod
    def setUpTestData(cls):
        cls.country_one = CountryFactory()
        cls.country_two = CountryFactory()

    def test_countries_list(self):
        self._test_list(
            user=None, expected_objects=[self.country_one, self.country_two],
        )

    def test_country_detail(self):
        self._test_retrieve(
            user=None, instance=self.country_one,
        )
