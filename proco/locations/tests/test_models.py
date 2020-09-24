from django.contrib.gis.geos import GEOSGeometry
from django.test import TestCase

from proco.locations.tests.factories import CountryFactory


class TestCountryModel(TestCase):
    def test_geometry_optimization_small_country(self):
        with open('proco/locations/tests/data/anquila.json') as geometry_file:
            country = CountryFactory(geometry=geometry_file.read())

        self.assertFalse(country.geometry_simplified.empty)
        self.assertNotEqual(country.geometry_simplified.num_points, country.geometry.num_points)

    def test_optimization_for_empty_geometry(self):
        country = CountryFactory(geometry=GEOSGeometry('{"type": "MultiPolygon", "coordinates": []}'))

        self.assertTrue(country.geometry.empty)
        self.assertTrue(country.geometry_simplified.empty)

    def test_geometry_null(self):
        country = CountryFactory(geometry=None)

        self.assertIsNone(country.geometry)
        self.assertIsNone(country.geometry_simplified)
