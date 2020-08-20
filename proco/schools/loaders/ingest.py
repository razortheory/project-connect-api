from datetime import date
from typing import Dict, Iterable, List

from django.contrib.gis.geos import Point
from django.utils.translation import ugettext_lazy as _

from proco.connection_statistics.models import SchoolWeeklyStatus
from proco.schools.loaders import csv as csv_loader
from proco.schools.loaders import xls as xls_loader
from proco.schools.models import School


def load_data(uploaded_file):
    if uploaded_file.name.endswith('.csv'):
        loader = csv_loader
    elif uploaded_file.name.endswith('.xls'):
        loader = xls_loader
    elif uploaded_file.name.endswith('.xlsx'):
        loader = xls_loader
    else:
        raise NotImplementedError

    return loader.load_file(uploaded_file)


def save_data(country, loaded: Iterable[Dict]) -> List[str]:
    errors = []

    for i, data in enumerate(loaded):
        row_index = i + 2  # enumerate starts from zero plus header
        # remove empty strings from data; ignore unicode from keys
        data = {key.encode('ascii', 'ignore').decode(): value for key, value in data.items() if value != ''}
        if not data:
            continue

        required_fields = {'name', 'lat', 'lon'}
        missing_fields = required_fields.difference(set(data.keys()))
        if missing_fields:
            errors.append(
                _('Row {0}: Missing data for required column(s) {1}').format(row_index, ', '.join(missing_fields))
            )
            continue

        school = None
        school_data = {
            'country': country,  # todo: calculate from point
        }
        history_data = {}

        if 'school_id' in data:
            school = School.objects.filter(external_id=data['school_id']).first()
            school_data['external_id'] = data['school_id']

        if not school:
            school = School.objects.filter(name=data['name']).first()

        if 'admin1' in data:
            school_data['admin_1_name'] = data['admin1']
        if 'admin2' in data:
            school_data['admin_2_name'] = data['admin2']
        if 'admin3' in data:
            school_data['admin_3_name'] = data['admin3']
        if 'admin4' in data:
            school_data['admin_4_name'] = data['admin4']

        school_data['name'] = data['name']

        try:
            school_data['geopoint'] = Point(x=float(data['lon']), y=float(data['lat']))
        except (TypeError, ValueError):
            errors.append(_('Row {0}: Bad data provided for geopoint').format(row_index))
            continue

        # static data
        if 'educ_level' in data:
            school_data['education_level'] = data['educ_level']
        if 'environment' in data:
            school_data['environment'] = data['environment']
        if 'address' in data:
            school_data['address'] = data['address']
        if 'type_school' in data:
            school_data['school_type'] = data['type_school']

        # historical data
        if 'num_students' in data:
            history_data['num_students'] = data['num_students']
        if 'num_teachers' in data:
            history_data['num_teachers'] = data['num_teachers']
        if 'num_classroom' in data:
            history_data['num_classroom'] = data['num_classroom']
        if 'num_latrines' in data:
            history_data['num_latrines'] = data['num_latrines']
        if 'electricity' in data:
            history_data['electricity_availability'] = data['electricity'].lower() in ['true', 'yes', '1']
        if 'computer_lab' in data:
            history_data['computer_lab'] = data['computer_lab'].lower() in ['true', 'yes', '1']
        if 'num_computers' in data:
            history_data['num_computers'] = data['num_computers']
        if 'connectivity' in data:
            history_data['connectivity'] = data['connectivity'].lower() in ['true', 'yes', '1']
        if 'type_connectivity' in data:
            history_data['connectivity_status'] = data['type_connectivity']
        if 'speed_connectivity' in data:
            history_data['connectivity_speed'] = data['speed_connectivity']
        if 'latency_connectivity' in data:
            history_data['connectivity_latency'] = data['latency_connectivity']
        if 'water' in data:
            history_data['running_water'] = data['water'].lower() in ['true', 'yes', '1']

        if school:
            for field, value in school_data.items():
                setattr(school, field, value)
                school.save()
        else:
            school = School.objects.create(**school_data)

        year, week_number, week_day = date.today().isocalendar()
        SchoolWeeklyStatus.objects.update_or_create(
            year=year, week=week_number, school=school, defaults=history_data,
        )

    return errors