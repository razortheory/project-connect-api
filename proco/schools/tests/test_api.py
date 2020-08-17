from django.test import TestCase

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

    def test_schools_list(self):
        self._test_list(
            user=None, expected_objects=[self.school_one, self.school_two],
        )

    def test_schools_detail(self):
        self._test_retrieve(
            user=None, instance=self.school_one,
        )

    def test_schools_list_filtered_by_country(self):
        SchoolFactory()
        self._test_list(
            user=None, expected_objects=[self.school_one, self.school_two],
            data={'country': self.country.id},
        )
