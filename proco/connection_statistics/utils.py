from datetime import timedelta

from django.db.models import Avg, Count, Q
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


def aggregate_real_time_data_to_school_daily_status(country):
    date = timezone.now().date()
    schools = RealTimeConnectivity.objects.filter(
        created__date=date, school__country=country,
    ).order_by('school').values_list('school', flat=True).order_by('school_id').distinct('school_id')

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


def aggregate_school_daily_to_country_daily(country) -> bool:
    date = timezone.now().date()

    aggregate = SchoolDailyStatus.objects.filter(
        school__country=country, date=date,
    ).aggregate(
        connectivity_speed__avg=Avg('connectivity_speed'),
        connectivity_latency__avg=Avg('connectivity_latency'),
    )
    if all(v is None for v in aggregate.values()):
        # nothing to do here
        return False

    CountryDailyStatus.objects.update_or_create(country=country, date=date, defaults={
        'connectivity_speed': aggregate['connectivity_speed__avg'],
        'connectivity_latency': aggregate['connectivity_latency__avg'],
    })

    return True


def aggregate_school_daily_status_to_school_weekly_status(country) -> bool:
    date = timezone.now().date()
    week_ago = date - timedelta(days=7)
    schools = School.objects.filter(
        country=country,
        id__in=SchoolDailyStatus.objects.filter(
            date__gte=week_ago,
        ).values_list('school', flat=True).order_by('school_id').distinct('school_id'),
    ).iterator()

    updated = False

    for school in schools:
        updated = True
        school_weekly, created = SchoolWeeklyStatus.objects.get_or_create(
            school=school, week=get_current_week(),
            year=get_current_year(),
        )

        aggregate = SchoolDailyStatus.objects.filter(
            school=school, date__gte=week_ago,
        ).aggregate(
            Avg('connectivity_speed'), Avg('connectivity_latency'),
        )

        school_weekly.connectivity = True
        school_weekly.connectivity_speed = aggregate['connectivity_speed__avg']
        school_weekly.connectivity_latency = aggregate['connectivity_latency__avg']

        prev_weekly = SchoolWeeklyStatus.objects.filter(school=school, date__lt=school_weekly.date).last()
        if prev_weekly:
            school_weekly.num_students = prev_weekly.num_students
            school_weekly.num_teachers = prev_weekly.num_teachers
            school_weekly.num_classroom = prev_weekly.num_classroom
            school_weekly.num_latrines = prev_weekly.num_latrines
            school_weekly.running_water = prev_weekly.running_water
            school_weekly.electricity_availability = prev_weekly.electricity_availability
            school_weekly.computer_lab = prev_weekly.computer_lab
            school_weekly.num_computers = prev_weekly.num_computers
            school_weekly.connectivity_type = prev_weekly.connectivity_type

        school_weekly.save()

    return updated


def update_country_weekly_status(country: Country):
    country_status, created = CountryWeeklyStatus.objects.get_or_create(
        country=country, year=get_current_year(), week=get_current_week(),
    )
    if created:
        country.last_weekly_status = country_status
        country.save()

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
        connectivity_speed=Avg('connectivity_speed', filter=Q(connectivity_speed__gt=0)),
        connectivity_latency=Avg('connectivity_latency', filter=Q(connectivity_latency__gt=0)),
    )

    country_status.connectivity_speed = schools_stats['connectivity_speed']
    country_status.connectivity_latency = schools_stats['connectivity_latency']

    overall_connected_schools = SchoolWeeklyStatus.objects.filter(
        school__country=country, connectivity=True,
    ).order_by('school_id').distinct('school_id').count()
    current_week_statuses = (
        schools_stats['connectivity_no'] +
        + schools_stats['connectivity_unknown']
        + schools_stats['connectivity_moderate']
        + schools_stats['connectivity_good']
    )

    country_status.schools_connectivity_no = schools_stats['connectivity_no']
    country_status.schools_connectivity_unknown = (
        schools_stats['connectivity_unknown']
        + (overall_connected_schools - current_week_statuses)
    )
    country_status.schools_connectivity_moderate = schools_stats['connectivity_moderate']
    country_status.schools_connectivity_good = schools_stats['connectivity_good']
    country_status.schools_connected = schools_stats['connectivity_moderate'] + schools_stats['connectivity_good']
    if country_status.schools_total:
        country_status.schools_with_data_percentage = 1.0 * overall_connected_schools / country_status.schools_total
    else:
        country_status.schools_with_data_percentage = 0

    if country_status.integration_status == CountryWeeklyStatus.SCHOOL_MAPPED and country_status.connectivity_speed:
        country_status.integration_status = CountryWeeklyStatus.STATIC_MAPPED
    if country_status.integration_status == CountryWeeklyStatus.STATIC_MAPPED and country.daily_status.exists():
        country_status.integration_status = CountryWeeklyStatus.REALTIME_MAPPED

    country_status.avg_distance_school = country.calculate_avg_distance_school()

    country_status.save()
