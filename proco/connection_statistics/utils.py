from datetime import datetime, timedelta

from django.db.models import Avg

from proco.connection_statistics.models import (
    CountryDailyStatus,
    CountryWeeklyStatus,
    RealTimeConnectivity,
    SchoolDailyStatus,
    SchoolWeeklyStatus,
)


def aggregate_real_time_data_to_school_daily_status():
    date = datetime.now().date()

    schools = RealTimeConnectivity.objects.all().order_by('school__name').values_list('school', flat=True).distinct()
    for school in schools:
        qs = RealTimeConnectivity.objects.filter(created__date=date, school=school)
        if qs.exists():
            aggregate = qs.aggregate(Avg('connectivity_speed'), Avg('connectivity_latency'))
            school_daily_status, _ = SchoolDailyStatus.objects.get_or_create(school_id=school, date=date)
            school_daily_status.connectivity_speed = aggregate['connectivity_speed__avg']
            school_daily_status.connectivity_latency = aggregate['connectivity_latency__avg']
            school_daily_status.save(update_fields=('connectivity_speed', 'connectivity_latency'))


def aggregate_real_time_data_to_country_daily_status():
    date = datetime.now().date()
    countries = RealTimeConnectivity.objects.all().order_by(
        'school__country__name',
    ).values_list(
        'school__country', flat=True,
    ).distinct()
    for country in countries:
        qs = RealTimeConnectivity.objects.filter(created__date=date, school__country=country)
        if qs.exists():
            aggregate = qs.aggregate(Avg('connectivity_speed'), Avg('connectivity_latency'))
            country_daily_status, _ = CountryDailyStatus.objects.get_or_create(country_id=country, date=date)
            country_daily_status.connectivity_speed = aggregate['connectivity_speed__avg']
            country_daily_status.connectivity_latency = aggregate['connectivity_latency__avg']
            country_daily_status.save(update_fields=('connectivity_speed', 'connectivity_latency'))


def aggregate_school_daily_status_to_school_weekly_status():
    date = (datetime.now() - timedelta(days=7)).date()
    schools = SchoolDailyStatus.objects.all().order_by('school__name').values_list('school', flat=True).distinct()
    for school in schools:
        qs_school_weekly = SchoolWeeklyStatus.objects.filter(school=school, week=date.isocalendar()[1])
        if qs_school_weekly.exists():
            school_weekly = qs_school_weekly.last()
        else:
            school_weekly = SchoolWeeklyStatus.objects.filter(school=school).last()
            school_weekly.id = None

        qs_country_daily_status = SchoolDailyStatus.objects.filter(school=school, date__gte=date)
        if qs_country_daily_status.exists():
            aggregate = qs_country_daily_status.aggregate(Avg('connectivity_speed'), Avg('connectivity_latency'))
            school_weekly.connectivity_speed = aggregate['connectivity_speed__avg']
            school_weekly.connectivity_latency = aggregate['connectivity_latency__avg']
            school_weekly.save()


def aggregate_country_daily_status_to_country_weekly_status():
    date = (datetime.now() - timedelta(days=7)).date()
    countries = CountryDailyStatus.objects.all().order_by('country__name').values_list('country', flat=True).distinct()
    for country in countries:
        qs_country_weekly = CountryWeeklyStatus.objects.filter(country=country, week=date.isocalendar()[1])
        if qs_country_weekly.exists():
            country_weekly = qs_country_weekly.last()
        else:
            country_weekly = CountryWeeklyStatus.objects.filter(country=country).last()
            country_weekly.id = None

        qs_country_daily_status = CountryDailyStatus.objects.filter(country=country, date__gte=date)
        if qs_country_daily_status.exists():
            aggregate = qs_country_daily_status.aggregate(Avg('connectivity_speed'), Avg('connectivity_latency'))
            country_weekly.connectivity_speed = aggregate['connectivity_speed__avg']
            country_weekly.connectivity_latency = aggregate['connectivity_latency__avg']
            country_weekly.save()
