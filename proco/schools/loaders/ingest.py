from typing import Iterable, Dict

from django.contrib.gis.geos import GEOSGeometry
from django.db import transaction

from proco.schools.models import School


@transaction.atomic
def save_data(country, loaded: Iterable[Dict], skip_errors=False):
    for data in list(loaded)[:1000]:
        # remove empty strings from data
        data = {key: value for key, value in data.items() if value != ''}

        if 'name' not in data:
            if skip_errors:
                continue
            else:
                pass
                # todo

        school = None
        school_data = {
            'country': country,  # todo: calculate from point
        }

        if 'school_id' in data:
            school = School.objects.filter(external_id=data['school_id']).first()
            school_data['external_id'] = data['school_id']

        if not school:
            school = School.objects.filter(name=data['name']).first()

        if 'admin2' in data:
            school_data['admin_2_name'] = data['admin2']
        if 'admin3' in data:
            school_data['admin_3_name'] = data['admin3']
        if 'admin4' in data:
            school_data['admin_4_name'] = data['admin4']

        school_data['name'] = data['name']
        if 'lat' not in data or 'lon' not in data:
            # we should return error here, but just skip for now
            if skip_errors:
                continue

        school_data['geopoint'] = GEOSGeometry("POINT({1} {0})".format(data['lat'], data['lon']))

        if 'educ_level' in data:
            school_data['education_level'] = data['educ_level']
        if 'environment' in data:
            school_data['environment'] = data['environment']
        if 'address' in data:
            school_data['address'] = data['address']
        if 'speed_connectivity' in data:
            # todo: write historical data
            pass

        if school:
            for field, value in school_data.items():
                setattr(school, field, value)
                school.save()
        else:
            school = School.objects.create(**school_data)

        print(school)

        # todo: save historical data
