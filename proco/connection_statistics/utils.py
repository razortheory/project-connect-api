from datetime import datetime, timedelta

from django.db.models import Avg, Count, F, FloatField, Func, Prefetch, Q
from django.utils import timezone

import numpy as np
from scipy.spatial.distance import pdist

from proco.connection_statistics.models import (
    CountryDailyStatus,
    CountryWeeklyStatus,
    RealTimeConnectivity,
    SchoolDailyStatus,
    SchoolWeeklyStatus,
)
from proco.locations.models import Country
from proco.utils.dates import get_current_week, get_current_year


def aggregate_real_time_data_to_school_daily_status(date=None):
    date = date or timezone.now().date()
    schools = RealTimeConnectivity.objects.filter(
        created__date=date,
    ).order_by('school').values_list('school', flat=True).order_by('school_id').distinct('school_id')

    for school in schools:
        aggregate = RealTimeConnectivity.objects.filter(
            created__date=date, school=school,
        ).aggregate(
            Avg('connectivity_speed'),
            Avg('connectivity_latency'),
        )
        school_daily_status, _ = SchoolDailyStatus.objects.get_or_create(school_id=school, date=date)
        school_daily_status.connectivity_speed = aggregate['connectivity_speed__avg'] or 0
        school_daily_status.connectivity_latency = aggregate['connectivity_latency__avg'] or 0
        school_daily_status.save()


def aggregate_school_daily_to_country_daily(date=None):
    date = date or timezone.now().date()
    for country in Country.objects.all():
        aggregate = SchoolDailyStatus.objects.filter(
            school__country=country, date=date,
        ).aggregate(
            connectivity_speed__avg=Avg('connectivity_speed'),
            connectivity_latency__avg=Avg('connectivity_latency'),
        )
        if all(v is None for v in aggregate.values()):
            # nothing to do here
            continue

        CountryDailyStatus.objects.update_or_create(country=country, date=date, defaults={
            'connectivity_speed': aggregate['connectivity_speed__avg'] or 0,
            'connectivity_latency': aggregate['connectivity_latency__avg'] or 0,
        })


def aggregate_school_daily_status_to_school_weekly_status(date=None):
    date = date or timezone.now().date()
    week_ago = date - timedelta(days=7)
    schools = SchoolDailyStatus.objects.filter(date__gte=week_ago).values_list(
        'school', flat=True,
    ).order_by('school_id').distinct('school_id')
    for school in schools:
        qs_school_weekly = SchoolWeeklyStatus.objects.filter(
            school=school, week=week_ago.isocalendar()[1],
            year=week_ago.isocalendar()[0],
        )
        if qs_school_weekly.exists():
            school_weekly = qs_school_weekly.last()
        else:
            school_weekly = SchoolWeeklyStatus.objects.filter(school=school).last()
            if school_weekly:
                if not (school_weekly.year == get_current_year() and school_weekly.week == get_current_week()):
                    # copy latest available one
                    school_weekly.id = None
                    school_weekly.year = get_current_year()
                    school_weekly.week = get_current_week()
            else:
                school_weekly = SchoolWeeklyStatus.objects.create(
                    school_id=school,
                    year=get_current_year(),
                    week=get_current_week(),
                    connectivity=True,
                )

        aggregate = SchoolDailyStatus.objects.filter(
            school=school, date__gte=week_ago,
        ).aggregate(
            Avg('connectivity_speed'), Avg('connectivity_latency'),
        )
        school_weekly.connectivity = bool(aggregate['connectivity_speed__avg'])
        school_weekly.connectivity_speed = aggregate['connectivity_speed__avg'] or 0
        school_weekly.connectivity_latency = aggregate['connectivity_latency__avg'] or 0
        school_weekly.save()


def _get_start_and_end_date_from_calendar_week(year, calendar_week):
    monday = datetime.strptime(f'{year}-{calendar_week}-1', '%Y-%W-%w').date()
    return monday, monday + timedelta(days=6.9)


def aggregate_country_daily_status_to_country_weekly_status(date=None):
    date = date or timezone.now().date()
    week_ago = date - timedelta(days=7)
    countries = CountryDailyStatus.objects.filter(
        date__gte=week_ago,
    ).order_by('country__name').values_list('country', flat=True).order_by('country_id').distinct('country_id')
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

        country.latest_status = [country_weekly]
        update_country_weekly_status(country, force=True)


def update_country_weekly_status(country: Country, force=False):
    if not hasattr(country, 'latest_status'):
        raise RuntimeError('country latest status should be prefetched')

    country_status = country.latest_status[0]
    if not force and not (country_status.year == get_current_year() and country_status.week == get_current_week()):
        # entry should be already updated
        return

    country_status.schools_total = country.schools.count()

    schools_stats = SchoolWeeklyStatus.objects.filter(
        year=country_status.year, week=country_status.week, school__country=country,
    ).aggregate(
        connectivity_no=Count(
            'connectivity_status', filter=Q(connectivity_status=SchoolWeeklyStatus.CONNECTIVITY_STATUSES.no),
        ),
        connectivity_unknown=Count(
            'connectivity_status', filter=Q(connectivity_status=SchoolWeeklyStatus.CONNECTIVITY_STATUSES.unknown),
        ),
        connectivity_moderate=Count(
            'connectivity_status', filter=Q(connectivity_status=SchoolWeeklyStatus.CONNECTIVITY_STATUSES.moderate),
        ),
        connectivity_good=Count(
            'connectivity_status', filter=Q(connectivity_status=SchoolWeeklyStatus.CONNECTIVITY_STATUSES.good),
        ),
        connectivity_speed=Avg('connectivity_speed'),
        connectivity_latency=Avg('connectivity_latency'),
    )

    country_status.connectivity_speed = schools_stats['connectivity_speed__avg'] or 0
    country_status.connectivity_latency = schools_stats['connectivity_latency__avg'] or 0

    overall_connected_schools = SchoolWeeklyStatus.objects.filter(
        school__country=country,
    ).order_by('school_id').distinct('school_id').count()
    current_week_statuses = (
        schools_stats['connectivity_no'] +
        + schools_stats['connectivity_unknown']
        + schools_stats['connectivity_moderate']
        + schools_stats['connectivity_good']
    )

    country_status.connectivity_no = schools_stats['connectivity_no']
    country_status.connectivity_unknown = (
        schools_stats['connectivity_unknown']
        + (overall_connected_schools - current_week_statuses)
    )
    country_status.connectivity_moderate = schools_stats['connectivity_moderate']
    country_status.connectivity_good = schools_stats['connectivity_good']
    country_status.schools_connected = country_status.connectivity_moderate + country_status.connectivity_good
    country_status.schools_with_data_percentage = 1.0 * overall_connected_schools / country_status.schools_total

    if country_status.integration_status in [
        CountryWeeklyStatus.STATIC_MAPPED, CountryWeeklyStatus.SCHOOL_MAPPED,
    ] and country_status.connectivity_speed:
        country_status.integration_status = CountryWeeklyStatus.REALTIME_MAPPED

    schools_points = list(country.schools.all().annotate(
        x=Func(F('geopoint'), function='ST_X', output_field=FloatField()),
        y=Func(F('geopoint'), function='ST_Y', output_field=FloatField()),
    ).values_list('x', 'y'))
    if schools_points:
        country_status.avg_distance_school = np.mean(pdist(schools_points))

    country_status.save()


def update_countries_weekly_statuses(force=False):
    countries = Country.objects.all().prefetch_related(
        Prefetch(
            'weekly_status',
            CountryWeeklyStatus.objects.order_by('country_id', '-year', '-week').distinct('country_id'),
            to_attr='latest_status',
        ),
    )
    for country in countries:
        update_country_weekly_status(country, force=force)


def update_specific_country_weekly_status(country: Country):
    country_weekly = CountryWeeklyStatus.objects.filter(
        country=country,
    ).order_by(
        'country_id', '-year', '-week',
    ).first()

    if not (country_weekly.year == get_current_year() and country_weekly.week == get_current_week()):
        # copy latest available one
        country.id = None
        country_weekly.year = get_current_year()
        country_weekly.week = get_current_week()
        country_weekly.save()

    country.latest_status = [country_weekly]
    update_country_weekly_status(country, force=True)
