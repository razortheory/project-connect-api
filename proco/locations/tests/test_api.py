from django.test import TestCase

from proco.connection_statistics.tests.factories import CountryWeeklyStatusFactory
from proco.locations.tests.factories import CountryFactory
from proco.schools.tests.factories import SchoolFactory
from proco.utils.tests import TestAPIViewSetMixin


class CountryApiTestCase(TestAPIViewSetMixin, TestCase):
    base_view = 'locations:countries'

    @classmethod
    def setUpTestData(cls):
        cls.country_one = CountryFactory()
        cls.country_two = CountryFactory()
        CountryWeeklyStatusFactory(country=cls.country_one)
        CountryWeeklyStatusFactory(country=cls.country_two)
        SchoolFactory(country=cls.country_one, location__country=cls.country_one)
        SchoolFactory(country=cls.country_one, location__country=cls.country_one)

    def test_countries_list(self):
        response = self._test_list(
            user=None, expected_objects=[self.country_one, self.country_two],
        )
        self.assertIn('integration_status', response.data[0])

    def test_country_detail(self):
        response = self._test_retrieve(
            user=None, instance=self.country_one,
        )
        self.assertIn('statistics', response.data)
