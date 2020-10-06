from datetime import datetime, timedelta

from django.contrib.gis.db.models.functions import GeoFunc
from django.db.models import Value

from proco.connection_statistics.models import (
    CountryDailyStatus,
    CountryWeeklyStatus,
    RealTimeConnectivity,
    SchoolDailyStatus,
    SchoolWeeklyStatus,
)
from proco.connection_statistics.tests.factories import (
    CountryDailyStatusFactory,
    CountryWeeklyStatusFactory,
    RealTimeConnectivityFactory,
    SchoolDailyStatusFactory,
    SchoolWeeklyStatusFactory,
)
from proco.locations.models import Country
from proco.schools.models import School
from proco.schools.tests.factories import SchoolFactory

AREA_COEFF = 223.4267  # coefficient of the average number of schools per unit area (250к/USA area)

NUMBER_DAYS_WEEKLY_STATISTICS = 365
NUMBER_DAYS_DAILY_STATISTICS = 365
NUMBER_DAYS_REALTIME_STATISTICS = 30


class GeneratePoints(GeoFunc):
    function = 'ST_GeneratePoints'


print('Data started to be generated')

total_schools_generated = 0
for country in Country.objects.all():
    if School.objects.filter(country=country).exists():
        continue
    total_schools_number = round(country.geometry.area * AREA_COEFF)
    if total_schools_number == 0:
        continue

    rand_points = list(
        Country.objects.filter(
            id=country.id,
        ).annotate(
            points=GeneratePoints('geometry', Value(total_schools_number)),
        ).first().points,
    )

    count = len(rand_points)
    if count:
        schools_generated = 0
        schools_obj = []

        for i in range(total_schools_number):
            school = SchoolFactory.build(
                name=f'{country.name}_school_{i}',
                country=country,
                location=country.country_location.all().first(),
                geopoint=rand_points[-count + i],
            )
            schools_generated += 1
            schools_obj.append(school)

            if schools_generated > 0 and schools_generated % 1000 == 0:
                School.objects.bulk_create(schools_obj)
                total_schools_generated += schools_generated
                schools_generated = 0
                schools_obj = []

        if schools_generated > 0:
            School.objects.bulk_create(schools_obj)
            total_schools_generated += schools_generated

    print(f'{country.name} schools created')

print(f'Schools generated - {total_schools_generated}')


schools = School.objects.all()
realtime_list = []
schools_daily_list = []
schools_weekly_list = []
schools_count = 0
for school in schools:
    for day in range(NUMBER_DAYS_REALTIME_STATISTICS):
        for hour in range(0, 20, 5):
            date = datetime.now() - timedelta(days=day, hours=hour)
            rt = RealTimeConnectivityFactory.build(school=school, created=date)
            realtime_list.append(rt)

    for day in range(NUMBER_DAYS_DAILY_STATISTICS):
        date = datetime.now() - timedelta(days=day)
        sd = SchoolDailyStatusFactory.build(school=school, created=date, date=date)
        schools_daily_list.append(sd)

    for day in range(0, NUMBER_DAYS_WEEKLY_STATISTICS, 7):
        date = datetime.now() - timedelta(days=day)
        year, week = date.isocalendar()[:2]
        sw = SchoolWeeklyStatusFactory.build(school=school, year=year, week=week)
        schools_weekly_list.append(sw)

    schools_count += 1

    if schools_count == 10:
        RealTimeConnectivity.objects.bulk_create(realtime_list)
        SchoolDailyStatus.objects.bulk_create(schools_daily_list)
        SchoolWeeklyStatus.objects.bulk_create(schools_weekly_list)
        schools_count = 0

if schools_count > 0:
    RealTimeConnectivity.objects.bulk_create(realtime_list)
    SchoolDailyStatus.objects.bulk_create(schools_daily_list)
    SchoolWeeklyStatus.objects.bulk_create(schools_weekly_list)


print('Schools statuses and realtime data generated')

for country in Country.objects.all():
    country_daily = []
    for day in range(NUMBER_DAYS_DAILY_STATISTICS):
        date = datetime.now() - timedelta(days=day)
        country_daily.append(CountryDailyStatusFactory.build(country=country, created=date, date=date))
    if country_daily:
        CountryDailyStatus.objects.bulk_create(country_daily)

    country_weekly = []
    for day in range(0, NUMBER_DAYS_WEEKLY_STATISTICS, 7):
        date = datetime.now() - timedelta(days=day)
        year, week = date.isocalendar()[:2]
        country_weekly.append(CountryWeeklyStatusFactory(country=country, year=year, week=week))
    if country_weekly:
        CountryWeeklyStatus.objects.bulk_create(country_weekly)

print('Countries statuses generated')
