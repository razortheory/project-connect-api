import random
from datetime import datetime, timedelta

from django.test import TestCase
from django.urls import reverse

from rest_framework import status

from proco.connection_statistics.models import (
    CountryDailyStatus,
    CountryWeeklyStatus,
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
    aggregate_real_time_data_to_country_daily_status,
    aggregate_real_time_data_to_school_daily_status,
    aggregate_school_daily_status_to_school_weekly_status,
)
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
        CountryWeeklyStatusFactory(country=cls.country_one, integration_status=CountryWeeklyStatus.REALTIME_MAPPED)
        CountryWeeklyStatusFactory(integration_status=CountryWeeklyStatus.STATIC_MAPPED)

    def test_global_stats(self):
        response = self.forced_auth_req(
            'get',
            reverse('connection_statistics:global-stat'),
        )
        correct_response = {
            'total_schools': 2,
            'schools_mapped': 1,
            'percent_schools_without_connectivity': 50.0,
            'countries_joined': 2,
            'countries_connected_to_realtime': 1,
            'countries_with_static_data': 1,
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, correct_response)

    def test_global_stats_queries(self):
        with self.assertNumQueries(5):
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
        CountryWeeklyStatusFactory(country=cls.country, date=(datetime.now() - timedelta(days=7)).date())
        SchoolWeeklyStatusFactory(school=cls.school, date=(datetime.now() - timedelta(days=7)).date())

    def test_aggregate_real_time_data_to_school_daily_status(self):
        aggregate_real_time_data_to_school_daily_status()
        self.assertEqual(SchoolDailyStatus.objects.count(), 1)
        self.assertEqual(SchoolDailyStatus.objects.first().connectivity_speed, 50.0)

    def test_aggregate_real_time_data_to_country_daily_status(self):
        aggregate_real_time_data_to_country_daily_status()
        self.assertEqual(CountryDailyStatus.objects.count(), 1)
        self.assertEqual(CountryDailyStatus.objects.first().connectivity_speed, 50.0)

    def test_aggregate_country_daily_status_to_country_weekly_status(self):
        CountryDailyStatusFactory(country=self.country, connectivity_speed=40.0, date=datetime.now().date())
        CountryDailyStatusFactory(country=self.country, connectivity_speed=60.0, date=datetime.now().date())
        aggregate_country_daily_status_to_country_weekly_status()
        self.assertEqual(CountryWeeklyStatus.objects.count(), 2)
        self.assertEqual(CountryWeeklyStatus.objects.last().connectivity_speed, 50.0)

    def test_aggregate_school_daily_status_to_school_weekly_status(self):
        SchoolDailyStatusFactory(school=self.school, connectivity_speed=40.0, date=datetime.now().date())
        SchoolDailyStatusFactory(school=self.school, connectivity_speed=60.0, date=datetime.now().date())
        aggregate_school_daily_status_to_school_weekly_status()
        self.assertEqual(SchoolWeeklyStatus.objects.count(), 2)
        self.assertEqual(SchoolWeeklyStatus.objects.last().connectivity_speed, 50.0)
