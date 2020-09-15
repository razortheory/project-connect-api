from django.utils import timezone

from celery.schedules import crontab
from celery.task import periodic_task

from proco.connection_statistics.utils import (
    aggregate_country_daily_status_to_country_weekly_status,
    aggregate_real_time_data_to_school_daily_status,
    aggregate_school_daily_status_to_school_weekly_status,
    aggregate_school_daily_to_country_daily,
)
from proco.schools.loaders.brasil_loader import brasil_statistic_loader


@periodic_task(run_every=crontab(hour='*/6', minute=0))
def aggregate_real_time_data():
    today = timezone.now().date()
    aggregate_real_time_data_to_school_daily_status(today)
    aggregate_school_daily_to_country_daily(today)


@periodic_task(run_every=crontab(hour=0, minute=0))
def aggregate_daily_statistics():
    aggregate_school_daily_status_to_school_weekly_status()
    aggregate_country_daily_status_to_country_weekly_status()


@periodic_task(run_every=crontab(hour='*/6', minute=0))
def load_brasil_daily_statistics():
    today = timezone.now().date()
    brasil_statistic_loader.update_schools()
    brasil_statistic_loader.update_statistic(today)
