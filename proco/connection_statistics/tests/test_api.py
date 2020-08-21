from django.test import TestCase
from django.urls import reverse

from rest_framework import status

from proco.connection_statistics.tests.factories import SchoolWeeklyStatusFactory
from proco.locations.tests.factories import CountryFactory
from proco.schools.tests.factories import SchoolFactory
from proco.utils.tests import TestAPIViewSetMixin


class GlobalStatisticsApiTestCase(TestAPIViewSetMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.country_one = CountryFactory()
        cls.school_one = SchoolFactory(country=cls.country_one, location__country=cls.country_one, geopoint=None)
        cls.school_two = SchoolFactory(country=cls.country_one, location__country=cls.country_one)
        SchoolWeeklyStatusFactory(school=cls.school_one, connectivity=True)
        SchoolWeeklyStatusFactory(school=cls.school_two, connectivity=False)

    def test_global_stats(self):
        response = self.forced_auth_req(
            'get',
            reverse('connection_statistics:global-stat'),
        )
        correct_response = {
            'total_schools': 2,
            'schools_mapped': 1,
            'percent_schools_without_connectivity': 50.0,
            'countries_joined': 1,
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, correct_response)

    def test_global_stats_queries(self):
        with self.assertNumQueries(4):
            self.forced_auth_req(
                'get',
                reverse('connection_statistics:global-stat'),
            )
