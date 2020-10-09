from django.contrib.gis.db.models.functions import GeoFunc
from django.core.management import BaseCommand
from django.db.models import Value

from proco.locations.models import Country
from proco.schools.models import School
from proco.schools.tests.factories import SchoolFactory

AREA_COEFF = 223.4267  # coefficient of the average number of schools per unit area (250к/USA area)

NUMBER_DAYS_WEEKLY_STATISTICS = 365
NUMBER_DAYS_DAILY_STATISTICS = 365
NUMBER_DAYS_REALTIME_STATISTICS = 30


class GeneratePoints(GeoFunc):
    function = 'ST_GeneratePoints'


class Command(BaseCommand):
    help = 'Generate schools.'

    def add_arguments(self, parser):
        parser.add_argument('country_id', type=str,
                            help="Please enter country id for specific country or 'all' for all countries")

    def handle(self, *args, **options):
        print('Data started to be generated')
        country_id = options.get('country_id')

        total_schools_generated = 0
        qs = Country.objects.all()
        if country_id.isdigit():
            qs = qs.filter(id=country_id)

        for country in qs:
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
