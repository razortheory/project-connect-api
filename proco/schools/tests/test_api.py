from django.test import TestCase
from django.urls import reverse

from rest_framework import status

from proco.connection_statistics.tests.factories import SchoolWeeklyStatusFactory
from proco.locations.tests.factories import CountryFactory
from proco.schools.tests.factories import SchoolFactory
from proco.utils.tests import TestAPIViewSetMixin


class SchoolsApiTestCase(TestAPIViewSetMixin, TestCase):
    base_view = 'schools:schools'

    @classmethod
    def setUpTestData(cls):
        cls.country = CountryFactory()
        cls.school_one = SchoolFactory(country=cls.country, location__country=cls.country)
        cls.school_two = SchoolFactory(country=cls.country, location__country=cls.country)
        SchoolWeeklyStatusFactory(school=cls.school_one)

    def test_schools_list(self):
        response = self.forced_auth_req(
            'get',
            reverse('schools:schools-list', args=[self.country.id]),
            user=None,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authorization_user(self):
        response = self.forced_auth_req(
            'get',
            reverse('schools:schools-list', args=[self.country.id]),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_schools_detail(self):
        response = self.forced_auth_req(
            'get',
            reverse('schools:schools-detail', args=[self.country.id, self.school_one.id]),
            user=None,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.school_one.id)
        self.assertIn('statistics', response.data)
