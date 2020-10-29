import csv

from django.contrib.gis.geos import Point
from django.core.management import BaseCommand

from proco.schools.models import School
from proco.locations.models import Country


class Command(BaseCommand):
    help = 'Clear the csv file from erroneous lines.'

    def add_arguments(self, parser):
        parser.add_argument('id_country', type=int)
        parser.add_argument('csv_file_name', type=str)

    def handle(self, *args, **options):
        id_country = options.get('id_country')
        csv_file_name = options.get('csv_file_name')

        with open(
            csv_file_name + '.csv', 'r', encoding='utf-8',
        ) as input_, open(
            csv_file_name + '_validate.csv', 'w',
        ) as output_:

            country = Country.objects.filter(id=id_country).first()
            if not country:
                print('Not found country id')
                return

            writer = csv.writer(output_)
            for i, row in enumerate(csv.DictReader(input_)):
                if i == 0:
                    writer.writerow(row)

                data = {key.encode('ascii', 'ignore').decode(): value for key, value in row.items() if value != ''}

                if not data:
                    continue

                required_fields = {'name', 'lat', 'lon'}
                missing_fields = required_fields.difference(set(data.keys()))
                if missing_fields:
                    continue

                if 'name' in data:
                    if len(data['name']) > School._meta.get_field('name').max_length:
                        continue
                if 'school_id' in data:
                    if len(data['school_id']) > School._meta.get_field('external_id').max_length:
                        continue
                if 'address' in data:
                    if len(data['address']) > School._meta.get_field('address').max_length:
                        continue
                if 'postal_code' in data:
                    if len(data['postal_code']) > School._meta.get_field('postal_code').max_length:
                        continue
                if 'educ_level' in data:
                    if len(data['educ_level']) > School._meta.get_field('education_level').max_length:
                        continue
                if 'environment' in data:
                    if len(data['environment']) > School._meta.get_field('environment').max_length:
                        continue
                if 'type_school' in data:
                    if len(data['type_school']) > School._meta.get_field('school_type').max_length:
                        continue

                try:
                    geopoint = Point(x=float(data['lon']), y=float(data['lat']))
                    if geopoint == Point(x=0, y=0):
                        continue
                    elif not country.geometry.contains(geopoint):
                        continue

                except (TypeError, ValueError):
                    continue

                if 'speed_connectivity' in data:
                    try:
                        float(data['speed_connectivity'])
                    except ValueError:
                        continue

                if 'environment' in data:
                    if data['environment'] not in dict(School.ENVIRONMENT_STATUSES).keys():
                        continue
                if 'num_students' in data:
                    print(type(data['num_students']))
                    if not data['num_students'].isdigit():
                        continue
                if 'num_teachers' in data:
                    if not data['num_teachers'].isdigit():
                        continue
                if 'num_classroom' in data:
                    if not data['num_classroom'].isdigit():
                        continue
                if 'num_latrines' in data:
                    if not data['num_latrines'].isdigit():
                        continue
                if 'latency_connectivity' in data:
                    if not data['latency_connectivity'].isdigit():
                        continue
                if 'num_computers' in data:
                    if data['num_computers'] < 0:
                        continue

                writer.writerow(row.values())
