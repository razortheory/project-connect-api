from datetime import timedelta

from django.core.cache import cache
from django.db.models import Sum
from django.test import TestCase
from django.utils import timezone

from proco.connection_statistics.models import RealTimeConnectivity
from proco.realtime_unicef.models import Measurement
from proco.realtime_unicef.tasks import sync_realtime_data
from proco.realtime_unicef.tests.db.test import init_test_db
from proco.realtime_unicef.tests.factories import MeasurementFactory
from proco.schools.tests.factories import SchoolFactory


class TasksTestCase(TestCase):
    databases = ['default', 'realtime']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        init_test_db()

    def setUp(self) -> None:
        super().setUp()
        cache.delete(Measurement.MEASUREMENT_DATE_CACHE_KEY)

    def test_empty_cache(self):
        school = SchoolFactory(external_id='test_1')
        MeasurementFactory(timestamp=timezone.now() - timedelta(days=1, hours=1), school_id='test_1', download=1)
        MeasurementFactory(timestamp=timezone.now() - timedelta(hours=23), school_id='test_1', download=2)

        sync_realtime_data()

        self.assertEqual(RealTimeConnectivity.objects.count(approx=False), 1)
        self.assertEqual(RealTimeConnectivity.objects.first().school, school)
        self.assertEqual(RealTimeConnectivity.objects.aggregate(speed=Sum('connectivity_speed'))['speed'], 2)

        self.assertGreater(Measurement.get_last_measurement_date(), timezone.now() - timedelta(hours=23, seconds=5))

    def test_cached_measurement_date(self):
        SchoolFactory(external_id='test_1')
        MeasurementFactory(timestamp=timezone.now() - timedelta(days=1, hours=1), school_id='test_1', download=1)
        MeasurementFactory(timestamp=timezone.now() - timedelta(hours=23), school_id='test_1', download=2)

        Measurement.set_last_measurement_date(timezone.now() - timedelta(days=1, hours=2))

        sync_realtime_data()

        self.assertEqual(RealTimeConnectivity.objects.count(approx=False), 2)
        self.assertEqual(RealTimeConnectivity.objects.aggregate(speed=Sum('connectivity_speed'))['speed'], 3)

    def test_idempotency(self):
        SchoolFactory(external_id='test_1')
        MeasurementFactory(timestamp=timezone.now(), school_id='test_1', download=1)
        MeasurementFactory(timestamp=timezone.now(), school_id='test_1', download=2)

        # two objects synchronized because they added after default last measurement date (day ago)
        sync_realtime_data()
        self.assertEqual(RealTimeConnectivity.objects.count(approx=False), 2)

        # no new entries added, because they are already synchronized
        RealTimeConnectivity.objects.all().delete()
        sync_realtime_data()
        self.assertEqual(RealTimeConnectivity.objects.count(approx=False), 0)

        # two previous entries synchronized again as we moved date back
        Measurement.set_last_measurement_date(timezone.now() - timedelta(hours=1))
        sync_realtime_data()
        self.assertEqual(RealTimeConnectivity.objects.count(approx=False), 2)
