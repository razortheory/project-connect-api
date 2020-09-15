from django.utils import timezone

from proco.connection_statistics.utils import (
    aggregate_country_daily_status_to_country_weekly_status,
    aggregate_real_time_data_to_school_daily_status,
    aggregate_school_daily_status_to_school_weekly_status,
    aggregate_school_daily_to_country_daily,
    update_countries_weekly_statuses,
)
from proco.schools.loaders.brasil_loader import brasil_statistic_loader
from proco.taskapp import app


@app.task(soft_time_limit=60 * 60, time_limit=60 * 60)
def aggregate_real_time_data():
    today = timezone.now().date()
    aggregate_real_time_data_to_school_daily_status(today)
    aggregate_school_daily_to_country_daily(today)


@app.task(soft_time_limit=10 * 60, time_limit=10 * 60)
def aggregate_daily_statistics():
    aggregate_school_daily_status_to_school_weekly_status()
    aggregate_country_daily_status_to_country_weekly_status()
    update_countries_weekly_statuses()


@app.task(soft_time_limit=60 * 60, time_limit=60 * 60)
def load_brasil_daily_statistics():
    today = timezone.now().date()
    brasil_statistic_loader.update_schools()
    brasil_statistic_loader.update_statistic(today)
