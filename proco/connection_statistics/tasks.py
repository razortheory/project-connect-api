from celery import chain

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
def aggregate_real_time_data(*args):
    aggregate_real_time_data_to_school_daily_status()
    aggregate_school_daily_to_country_daily()


@app.task(soft_time_limit=10 * 60, time_limit=10 * 60)
def aggregate_daily_statistics(*args):
    aggregate_school_daily_status_to_school_weekly_status()
    aggregate_country_daily_status_to_country_weekly_status()
    update_countries_weekly_statuses()


@app.task(soft_time_limit=60 * 60, time_limit=60 * 60)
def update_brasil_schools():
    brasil_statistic_loader.update_schools()


@app.task(soft_time_limit=60 * 60, time_limit=60 * 60)
def test_celery():
    print ("!" * 100)
    print("OK")
    print ("!" * 100)


@app.task(soft_time_limit=30 * 60, time_limit=30 * 60)
def load_brasil_daily_statistics(*args):
    # would be good to separate schools loading from statistics and run once a day
    brasil_statistic_loader.update_statistic()


@app.task
def load_data_from_unicef_db(*args):
    # just dummy to make tasks structure
    return


@app.task
def update_real_time_data():
    chain(
        # it would be better to use group, but we need result backend to be configured
        # group(load_data_from_unicef_db.s(), load_brasil_daily_statistics.s()),
        load_data_from_unicef_db.s(),
        load_brasil_daily_statistics.s(),
        aggregate_real_time_data.s(),
        aggregate_daily_statistics.s(),
    ).delay()
