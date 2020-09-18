from datetime import datetime, timedelta

from django.db.models import Avg, Prefetch
from django.utils import timezone

from proco.connection_statistics.models import (
    CountryDailyStatus,
    CountryWeeklyStatus,
    RealTimeConnectivity,
    SchoolDailyStatus,
    SchoolWeeklyStatus,
)
from proco.locations.models import Country
from proco.schools.models import School
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
        qs_school_weekly = SchoolWeeklyStatus.objects.filter(school=school, week=week_ago.isocalendar()[1])
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

        aggregate = CountryDailyStatus.objects.filter(
            country=country, date__gte=week_ago,
        ).aggregate(
            Avg('connectivity_speed'), Avg('connectivity_latency'),
        )
        country_weekly.connectivity_speed = aggregate['connectivity_speed__avg'] or 0
        country_weekly.connectivity_latency = aggregate['connectivity_latency__avg'] or 0

        week_start, week_end = _get_start_and_end_date_from_calendar_week(country_weekly.year, country_weekly.week)
        schools_number = School.objects.filter(created__lte=week_end, country=country_weekly.country).count()
        if schools_number:
            schools_with_data_number = School.objects.filter(
                weekly_status__created__lte=week_end, country=country_weekly.country,
            ).count()
            country_weekly.schools_with_data_percentage = 100.0 * schools_with_data_number / schools_number

        if country_weekly.integration_status in [
            CountryWeeklyStatus.STATIC_MAPPED, CountryWeeklyStatus.SCHOOL_MAPPED,
        ] and aggregate['connectivity_speed__avg']:
            country_weekly.integration_status = CountryWeeklyStatus.REALTIME_MAPPED
        country_weekly.save()


def update_country_weekly_status(country: Country, force=False):
    if not hasattr(country, 'latest_status'):
        raise RuntimeError('country latest status should be prefetched')

    country_status = country.latest_status[0]
    if not force and not (country_status.year == get_current_year() and country_status.week == get_current_week()):
        # entry should be already updated
        return

    statistics = {
        'schools_total': 0,
        'schools_connected': 0,
        'schools_connectivity_no': 0,
        'schools_connectivity_unknown': 0,
        'schools_connectivity_moderate': 0,
        'schools_connectivity_good': 0,
    }
    country_schools = country.schools.all().prefetch_related(
        Prefetch(
            'weekly_status',
            SchoolWeeklyStatus.objects.order_by('school_id', '-year', '-week').distinct('school_id'),
            to_attr='latest_status',
        ),
    )

    # slower but much easier to work with
    for school in country_schools:
        statistics['schools_total'] += 1
        if not school.latest_status:
            statistics['schools_connectivity_unknown'] += 1
            continue

        latest_status = school.latest_status[0]
        connectivity_status = latest_status.get_connectivity_status()
        if connectivity_status == SchoolWeeklyStatus.CONNECTIVITY_STATUSES.no:
            statistics['schools_connectivity_no'] += 1
        elif connectivity_status == SchoolWeeklyStatus.CONNECTIVITY_STATUSES.unknown:
            statistics['schools_connectivity_unknown'] += 1
            statistics['schools_connected'] += 1
        elif connectivity_status == SchoolWeeklyStatus.CONNECTIVITY_STATUSES.moderate:
            statistics['schools_connectivity_moderate'] += 1
            statistics['schools_connected'] += 1
        elif connectivity_status == SchoolWeeklyStatus.CONNECTIVITY_STATUSES.good:
            statistics['schools_connectivity_good'] += 1
            statistics['schools_connected'] += 1

    for field, value in statistics.items():
        setattr(country_status, field, value)

    # todo: calculate
    country_status.avg_distance_school = 0

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
