from django.utils import timezone

from celery import chain, chord, group

from proco.connection_statistics.models import CountryDailyStatus
from proco.connection_statistics.utils import (
    aggregate_country_daily_status_to_country_weekly_status,
    aggregate_real_time_data_to_school_daily_status,
    aggregate_school_daily_status_to_school_weekly_status,
    aggregate_school_daily_to_country_daily,
    update_countries_weekly_statuses,
    update_specific_country_weekly_status,
)
from proco.locations.models import Country
from proco.schools.loaders.brasil_loader import brasil_statistic_loader
from proco.taskapp import app


@app.task(soft_time_limit=60 * 60, time_limit=60 * 60)
def aggregate_real_time_data(*args):
    aggregate_real_time_data_to_school_daily_status()
    aggregate_school_daily_to_country_daily()


@app.task(soft_time_limit=10 * 60, time_limit=60 * 60)
def aggregate_daily_statistics(country_id, *args):
    aggregate_school_daily_status_to_school_weekly_status(country_id)
    week_ago = timezone.now().date() - timezone.timedelta(days=7)
    if CountryDailyStatus.objects.filter(
        country_id=country_id,
        date__gte=week_ago,
    ).exists():
        aggregate_country_daily_status_to_country_weekly_status(country_id)


@app.task(soft_time_limit=10 * 60, time_limit=60 * 60)
def update_countries_weekly_statuses_task(*args):
    update_countries_weekly_statuses()


@app.task(soft_time_limit=10 * 60, time_limit=60 * 60)
def update_specific_country_weekly_statuses_task(_prev_status, country_id, *args):
    country = Country.objects.get(id=country_id)
    update_specific_country_weekly_status(country)


@app.task(soft_time_limit=60 * 60, time_limit=60 * 60)
def update_brasil_schools():
    brasil_statistic_loader.update_schools()


@app.task(soft_time_limit=30 * 60, time_limit=30 * 60)
def load_brasil_daily_statistics(*args):
    brasil_statistic_loader.update_statistic()


@app.task
def load_data_from_unicef_db(*args):
    # just dummy to make tasks structure
    return


@app.task
def finalize_task():
    return 'Done'


@app.task
def update_real_time_data():
    countries_ids = Country.objects.values_list('id', flat=True)

    chain(
        load_data_from_unicef_db.s(),
        load_brasil_daily_statistics.s(),
        aggregate_real_time_data.s(),
        chord(
            group([
                aggregate_daily_statistics.s(country_id)
                for country_id in countries_ids
            ]),
            finalize_task.si(),
        ),
        chord(
            group([
                update_specific_country_weekly_statuses_task.s(country_id)
                for country_id in countries_ids
            ]),
            finalize_task.si(),
        ),
    ).delay()
