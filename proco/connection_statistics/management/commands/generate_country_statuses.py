from datetime import datetime, timedelta

from proco.connection_statistics.models import CountryDailyStatus, CountryWeeklyStatus
from proco.connection_statistics.tests.factories import CountryDailyStatusFactory, CountryWeeklyStatusFactory
from proco.locations.models import Country

NUMBER_DAYS_WEEKLY_STATISTICS = 90
NUMBER_DAYS_DAILY_STATISTICS = 90


print('Countries statuses generate started')

for country in Country.objects.all():
    country_daily = []
    for day in range(NUMBER_DAYS_DAILY_STATISTICS):
        date = datetime.now() - timedelta(days=day)
        country_daily.append(CountryDailyStatusFactory.build(country=country, created=date, date=date))
    if country_daily:
        CountryDailyStatus.objects.bulk_create(country_daily)
        country_daily = []

    country_weekly = []
    for day in range(0, NUMBER_DAYS_WEEKLY_STATISTICS, 7):
        date = datetime.now() - timedelta(days=day)
        year, week = date.isocalendar()[:2]
        country_weekly.append(CountryWeeklyStatusFactory.build(country=country, year=year, week=week, date=date))
    if country_weekly:
        CountryWeeklyStatus.objects.bulk_create(country_weekly)
        country_weekly = []

    print(f'{country.name} generated')

print('Countries statuses generated')
