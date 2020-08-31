from datetime import date

from django.test import TestCase

from rest_framework import status

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
        year, week_number, week_day = date.today().isocalendar()
        CountryWeeklyStatusFactory(country=cls.country_one, year=year, week=week_number)
        SchoolFactory(country=cls.country_one, location__country=cls.country_one)
        SchoolFactory(country=cls.country_one, location__country=cls.country_one)

    def test_countries_list(self):
        with self.assertNumQueries(2):
            response = self._test_list(
                user=None, expected_objects=[self.country_one, self.country_two],
            )
        self.assertIn('integration_status', response.data[0])

    def test_country_detail(self):
        with self.assertNumQueries(2):
            response = self._test_retrieve(
                user=None, instance=self.country_one,
            )
        self.assertIn('statistics', response.data)

    def test_country_list_cached(self):
        with self.assertNumQueries(2):
            response = self._test_list(
                user=None, expected_objects=[self.country_one, self.country_two],
            )
            etag = response._headers.get('etag', None)
            self.assertTrue(etag)

        with self.assertNumQueries(0):
            headers = {'HTTP_IF_NONE_MATCH': etag[1]}
            self._test_list(
                user=None,
                expected_objects=[self.country_one, self.country_two],
                expected_status=status.HTTP_304_NOT_MODIFIED,
                **headers,
            )
