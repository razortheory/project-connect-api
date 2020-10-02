from datetime import datetime, timedelta

from django.contrib.gis.db.models.functions import GeoFunc
from django.db import IntegrityError
from django.db.models import Value

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


for country in Country.objects.all():
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
        for i in range(total_schools_number):
            SchoolFactory(
                name=f'{country.name}_school_{i}',
                country=country,
                location=country.country_location.all().first(),
                geopoint=rand_points[-count + i],
            )


schools = School.objects.all()

for school in schools:
    for day in range(NUMBER_DAYS_REALTIME_STATISTICS):
        for hour in range(0, 20, 5):
            date = datetime.now() - timedelta(days=day, hours=hour)
            RealTimeConnectivityFactory(school=school, created=date)

    for day in range(NUMBER_DAYS_DAILY_STATISTICS):
        date = datetime.now() - timedelta(days=day)
        try:
            SchoolDailyStatusFactory(school=school, created=date, date=date)
        except IntegrityError:
            continue

    for day in range(0, NUMBER_DAYS_WEEKLY_STATISTICS, 7):
        date = datetime.now() - timedelta(days=day)
        year, week = date.isocalendar()[:2]
        try:
            SchoolWeeklyStatusFactory(school=school, year=year, week=week)
        except IntegrityError:
            continue

for country in Country.objects.all():
    for day in range(NUMBER_DAYS_DAILY_STATISTICS):
        date = datetime.now() - timedelta(days=day)
        try:
            CountryDailyStatusFactory(country=country, created=date, date=date)
        except IntegrityError:
            continue

    for day in range(0, NUMBER_DAYS_WEEKLY_STATISTICS, 7):
        date = datetime.now() - timedelta(days=day)
        year, week = date.isocalendar()[:2]
        try:
            CountryWeeklyStatusFactory(country=country, year=year, week=week)
        except IntegrityError:
            continue
