from datetime import datetime, timedelta

from django.db.models import Avg
from django.utils import timezone

from proco.connection_statistics.models import (
    CountryDailyStatus,
    CountryWeeklyStatus,
    RealTimeConnectivity,
    SchoolDailyStatus,
    SchoolWeeklyStatus,
)
from proco.locations.models import Country
from proco.utils.dates import get_current_week, get_current_year


def aggregate_real_time_data_to_school_daily_status():
    date = datetime.now().date()

    schools = RealTimeConnectivity.objects.filter(
        created__date=date,
    ).order_by('school').values_list('school', flat=True).distinct()

    for school in schools:
        aggregate = RealTimeConnectivity.objects.filter(
            created__date=date, school=school,
        ).aggregate(
            Avg('connectivity_speed'),
            Avg('connectivity_latency'),
        )
        school_daily_status, _ = SchoolDailyStatus.objects.get_or_create(school_id=school, date=date)
        school_daily_status.connectivity_speed = aggregate['connectivity_speed__avg']
        school_daily_status.connectivity_latency = aggregate['connectivity_latency__avg']
        school_daily_status.save()


def aggregate_school_daily_to_country_daily():
    today = timezone.now().date()
    for country in Country.objects.all():
        aggregate = SchoolDailyStatus.objects.filter(
            school__country=country, date=today,
        ).aggregate(
            connectivity_speed__avg=Avg('connectivity_speed'),
            connectivity_latency__avg=Avg('connectivity_latency'),
        )
        if all(v is None for v in aggregate.values()):
            # nothing to do here
            continue

        CountryDailyStatus.objects.update_or_create(country=country, date=today, defaults={
            'connectivity_speed': aggregate['connectivity_speed__avg'],
            'connectivity_latency': aggregate['connectivity_latency__avg'],
        })


def aggregate_school_daily_status_to_school_weekly_status():
    date = (datetime.now() - timedelta(days=7)).date()
    schools = SchoolDailyStatus.objects.all().order_by('school__name').values_list('school', flat=True).distinct()
    for school in schools:
        qs_school_weekly = SchoolWeeklyStatus.objects.filter(school=school, week=date.isocalendar()[1])
        if qs_school_weekly.exists():
            school_weekly = qs_school_weekly.last()
        else:
            school_weekly = SchoolWeeklyStatus.objects.filter(school=school).last()
            if school_weekly:
                # copy latest available one
                school_weekly.id = None
                school_weekly.year = get_current_year()
                school_weekly.week = get_current_week()
            else:
                school_weekly = SchoolWeeklyStatus.objects.create(
                    school=school,
                    year=get_current_year(),
                    week=get_current_week(),
                )

        qs_country_daily_status = SchoolDailyStatus.objects.filter(school=school, date__gte=date)
        if qs_country_daily_status.exists():
            aggregate = qs_country_daily_status.aggregate(Avg('connectivity_speed'), Avg('connectivity_latency'))
            school_weekly.connectivity_speed = aggregate['connectivity_speed__avg']
            school_weekly.connectivity_latency = aggregate['connectivity_latency__avg']
            school_weekly.save()
            school_weekly.reset_date_fields()


def aggregate_country_daily_status_to_country_weekly_status():
    week_ago = (datetime.now() - timedelta(days=7)).date()
    countries = CountryDailyStatus.objects.filter(
        date__gte=week_ago,
    ).order_by('country__name').values_list('country', flat=True).distinct()
    for country in countries:
        country_weekly = CountryWeeklyStatus.objects.filter(
            country=country, year=get_current_year(), week=get_current_week(),
        ).first()
        if not country_weekly:
            country_weekly = CountryWeeklyStatus.objects.filter(country=country).order_by('year', 'week').last()
            # copy latest available one
            country_weekly.id = None
            country_weekly.year = get_current_year()
            country_weekly.week = get_current_week()

        aggregate = CountryDailyStatus.objects.filter(
            country=country, date__gte=week_ago,
        ).aggregate(
            Avg('connectivity_speed'), Avg('connectivity_latency'),
        )
        country_weekly.connectivity_speed = aggregate['connectivity_speed__avg']
        country_weekly.connectivity_latency = aggregate['connectivity_latency__avg']
        if country_weekly.integration_status in [
            CountryWeeklyStatus.STATIC_MAPPED, CountryWeeklyStatus.SCHOOL_MAPPED,
        ] and aggregate['connectivity_speed__avg']:
            country_weekly.integration_status = CountryWeeklyStatus.REALTIME_MAPPED
        country_weekly.save()
        country_weekly.reset_date_fields()
