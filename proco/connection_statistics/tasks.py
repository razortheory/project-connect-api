from datetime import datetime

from django.db.models import Avg

from celery.schedules import crontab
from celery.task import periodic_task

from proco.connection_statistics.models import (
    CountryDailyStatus,
    RealTimeConnectivity,
    SchoolDailyStatus,
    SchoolWeeklyStatus,
)


@periodic_task(run_every=crontab(hour='*/6'))
def aggregate_real_time_data():
    date = datetime.now().date()

    schools = RealTimeConnectivity.objects.all().order_by('name').values_list('school', flat=True).distinct()
    for school in schools.iterator():
        qs = RealTimeConnectivity.objects.filter(created__date=date, school=school)
        if qs.exists():
            aggregate = qs.aggregate(Avg('connectivity_speed'), Avg('cconnectivity_latency'))
            school_daily_status, _ = SchoolDailyStatus.objects.get_or_create(school=school, date=date)
            school_daily_status.connectivity_speed = aggregate['connectivity_speed__avg']
            school_daily_status.connectivity_latency = aggregate['connectivity_latency__avg']
            school_daily_status.save(update_fields=('connectivity_speed', 'connectivity_latency'))

    countries = RealTimeConnectivity.objects.all()\
        .order_by('school')\
        .values_list('school__country', flat=True)\
        .distinct()
    for country in countries:
        qs = RealTimeConnectivity.objects.filter(created__date=date, school__country=country)
        if qs.exists():
            aggregate = qs.aggregate(Avg('connectivity_speed'), Avg('cconnectivity_latency'))
            country_daily_status, _ = CountryDailyStatus.objects.get_or_create(country=country, date=date)
            country_daily_status.connectivity_speed = aggregate['connectivity_speed__avg']
            country_daily_status.connectivity_latency = aggregate['connectivity_latency__avg']
            country_daily_status.save(update_fields=('connectivity_speed', 'connectivity_latency'))

    schools = SchoolDailyStatus.objects.all().order_by('school__name').values_list('school', flat=True).distinct()
    for school in schools:
        qs_school_weekly = SchoolWeeklyStatus.objects.filter(school=school, week=date.isocalendar()[1])
        if qs_school_weekly.exists():
            school_weekly = qs_school_weekly.first()
        else:
            school_weekly = SchoolWeeklyStatus.objects.filter(school=school).order_by('-week').first()
            school_weekly.id = None
