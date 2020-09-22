import json
import os
import random
from datetime import datetime, timedelta
from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from rest_framework import status

from pytz import UTC

from proco.connection_statistics.models import (
    CountryDailyStatus,
    CountryWeeklyStatus,
    RealTimeConnectivity,
    SchoolDailyStatus,
    SchoolWeeklyStatus,
)
from proco.connection_statistics.tests.factories import (
    CountryDailyStatusFactory,
    CountryWeeklyStatusFactory,
    RealTimeConnectivityFactory,
    SchoolDailyStatusFactory,
    SchoolWeeklyStatusFactory,
)
from proco.connection_statistics.utils import (
    aggregate_country_daily_status_to_country_weekly_status,
    aggregate_real_time_data_to_school_daily_status,
    aggregate_school_daily_status_to_school_weekly_status,
    aggregate_school_daily_to_country_daily,
)
from proco.locations.tests.factories import CountryFactory
from proco.schools.loaders.brasil_loader import brasil_statistic_loader
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
        CountryWeeklyStatusFactory(country=cls.country_one, integration_status=CountryWeeklyStatus.REALTIME_MAPPED,
                                   year=2020)
        cls.cws = CountryWeeklyStatusFactory(integration_status=CountryWeeklyStatus.STATIC_MAPPED, year=2021)

    def setUp(self):
        cache.clear()
        super().setUp()

    def test_global_stats(self):
        response = self.forced_auth_req(
            'get',
            reverse('connection_statistics:global-stat'),
        )
        correct_response = {
            'total_schools': 2,
            'schools_mapped': 1,
            'percent_schools_without_connectivity': 0.5,
            'countries_joined': 2,
            'countries_connected_to_realtime': 1,
            'countries_with_static_data': 1,
            'last_date_updated': self.cws.date.strftime('%B %Y'),
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, correct_response)

    def test_global_stats_queries(self):
        with self.assertNumQueries(6):
            self.forced_auth_req(
                'get',
                reverse('connection_statistics:global-stat'),
            )
        with self.assertNumQueries(0):
            self.forced_auth_req(
                'get',
                reverse('connection_statistics:global-stat'),
            )


class CountryWeekStatsApiTestCase(TestAPIViewSetMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.country_one = CountryFactory()
        cls.country_two = CountryFactory()
        cls.stat_one = CountryWeeklyStatusFactory(country=cls.country_one)
        cls.stat_two = CountryWeeklyStatusFactory(country=cls.country_two)

    def test_country_weekly_stats(self):
        response = self.forced_auth_req(
            'get',
            reverse('connection_statistics:country-weekly-stat', kwargs={
                'country_id': self.stat_one.country_id,
                'year': self.stat_one.year,
                'week': self.stat_one.week,
            }),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['schools_total'], self.stat_one.schools_total)
        self.assertEqual(response.data['avg_distance_school'], self.stat_one.avg_distance_school)
        self.assertEqual(response.data['schools_connected'], self.stat_one.schools_connected)
        self.assertEqual(response.data['schools_connectivity_unknown'], self.stat_one.schools_connectivity_unknown)
        self.assertEqual(response.data['schools_connectivity_moderate'], self.stat_one.schools_connectivity_moderate)
        self.assertEqual(response.data['schools_connectivity_good'], self.stat_one.schools_connectivity_good)
        self.assertEqual(response.data['schools_connectivity_no'], self.stat_one.schools_connectivity_no)
        self.assertEqual(response.data['integration_status'], self.stat_one.integration_status)

    def test_country_weekly_stats_queries(self):
        with self.assertNumQueries(1):
            self.forced_auth_req(
                'get',
                reverse('connection_statistics:country-weekly-stat', kwargs={
                    'country_id': self.stat_one.country_id,
                    'year': self.stat_one.year,
                    'week': self.stat_one.week,
                }),
            )


class CountryDailyStatsApiTestCase(TestAPIViewSetMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.country_one = CountryFactory()
        cls.country_two = CountryFactory()

        cls.country_one_stats_number = random.SystemRandom().randint(a=5, b=25)
        for _i in range(cls.country_one_stats_number):
            CountryDailyStatusFactory(country=cls.country_one)

        CountryDailyStatusFactory(country=cls.country_two)

    def test_country_weekly_stats(self):
        response = self.forced_auth_req(
            'get',
            reverse('connection_statistics:country-daily-stat', kwargs={
                'country_id': self.country_one.id,
            }),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], self.country_one_stats_number)

        response = self.forced_auth_req(
            'get',
            reverse('connection_statistics:country-daily-stat', kwargs={
                'country_id': self.country_two.id,
            }),
        )
        self.assertEqual(response.data['count'], 1)

    def test_country_weekly_stats_queries(self):
        with self.assertNumQueries(2):
            self.forced_auth_req(
                'get',
                reverse('connection_statistics:country-daily-stat', kwargs={
                    'country_id': self.country_one.id,
                }),
            )


class AggregateConnectivityDataTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.country = CountryFactory()
        cls.school = SchoolFactory(country=cls.country)
        RealTimeConnectivityFactory(school=cls.school, connectivity_speed=40.0)
        RealTimeConnectivityFactory(school=cls.school, connectivity_speed=60.0)
        year, week, weekday = (datetime.now() - timedelta(days=7)).date().isocalendar()
        SchoolWeeklyStatusFactory(school=cls.school, year=year, week=week)

    def test_aggregate_real_time_data_to_school_daily_status(self):
        today = datetime.now().date()
        aggregate_real_time_data_to_school_daily_status(today)
        self.assertEqual(SchoolDailyStatus.objects.count(), 1)
        self.assertEqual(SchoolDailyStatus.objects.first().connectivity_speed, 50.0)

    def test_aggregate_real_time_data_to_country_daily_status(self):
        today = datetime.now().date()
        aggregate_real_time_data_to_school_daily_status(today)
        aggregate_school_daily_to_country_daily(today)
        self.assertEqual(CountryDailyStatus.objects.count(), 1)
        self.assertEqual(CountryDailyStatus.objects.first().connectivity_speed, 50.0)

    def test_aggregate_school_daily_to_country_daily(self):
        today = datetime.now().date()
        SchoolDailyStatusFactory(school__country=self.country, connectivity_speed=40.0, date=today)
        SchoolDailyStatusFactory(school__country=self.country, connectivity_speed=60.0, date=today)

        aggregate_school_daily_to_country_daily(today)
        self.assertEqual(CountryDailyStatus.objects.get(country=self.country, date=today).connectivity_speed, 50.0)

    def test_aggregate_country_daily_status_to_country_weekly_status(self):
        today = datetime.now().date()
        CountryDailyStatusFactory(country=self.country, connectivity_speed=40.0, date=today - timedelta(days=1))
        CountryDailyStatusFactory(country=self.country, connectivity_speed=60.0, date=today)

        aggregate_country_daily_status_to_country_weekly_status()
        self.assertEqual(CountryWeeklyStatus.objects.filter(country=self.country).count(), 1)
        self.assertEqual(CountryWeeklyStatus.objects.filter(country=self.country).last().connectivity_speed, 50.0)

        country_weekly = CountryWeeklyStatus.objects.filter(country=self.country).last()
        self.assertEqual(country_weekly.integration_status, CountryWeeklyStatus.REALTIME_MAPPED)

    def test_aggregate_school_daily_status_to_school_weekly_status(self):
        today = datetime.now().date()
        SchoolDailyStatusFactory(school=self.school, connectivity_speed=40.0, date=today - timedelta(days=1))
        SchoolDailyStatusFactory(school=self.school, connectivity_speed=60.0, date=today)

        aggregate_school_daily_status_to_school_weekly_status()
        self.assertEqual(SchoolWeeklyStatus.objects.count(), 1)
        self.assertEqual(SchoolWeeklyStatus.objects.last().connectivity_speed, 50.0)


class TestBrazilParser(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        with open(os.path.join('proco', 'connection_statistics', 'tests', 'data', 'brazil_example.json')) as example:
            cls.example_data = json.load(example)
        cls.country = CountryFactory(code='BR')

    @patch('proco.schools.loaders.brasil_loader.BrasilSimnetLoader.load_schools_statistic')
    def test_unknown_schools(self, load_mock):
        load_mock.return_value = self.example_data

        today = datetime.now().date()
        brasil_statistic_loader.update_statistic(today)
        self.assertEqual(RealTimeConnectivity.objects.filter(school__country=self.country).count(), 0)

    @patch('proco.schools.loaders.brasil_loader.BrasilSimnetLoader.load_schools_statistic')
    def test_data_loaded(self, load_mock):
        load_mock.return_value = self.example_data
        SchoolFactory(country=self.country, external_id=43029094)
        SchoolFactory(country=self.country, external_id=41062310)
        today = datetime.now().date()

        with self.assertNumQueries(6):
            brasil_statistic_loader.update_statistic(today)

        # records shouldn't be saved during second call, so there are less queries expected
        with self.assertNumQueries(4):
            brasil_statistic_loader.update_statistic(today)

        self.assertEqual(RealTimeConnectivity.objects.filter(school__country=self.country).count(), 3)
        self.assertListEqual(
            list(
                RealTimeConnectivity.objects.filter(
                    school__country=self.country,
                ).order_by('created').values_list('created', flat=True),
            ),
            [
                datetime(year=2020, month=9, day=15, hour=1, minute=10, second=37, tzinfo=UTC),
                datetime(year=2020, month=9, day=15, hour=5, minute=16, second=36, tzinfo=UTC),
                datetime(year=2020, month=9, day=15, hour=7, minute=16, second=36, tzinfo=UTC),
            ],
        )
