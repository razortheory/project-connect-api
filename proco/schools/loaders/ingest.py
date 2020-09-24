from datetime import date
from typing import Dict, Iterable, List, Tuple

from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.utils.formats import sanitize_separators
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


def save_data(country, loaded: Iterable[Dict]) -> Tuple[List[str], List[str]]:
    warnings = []
    errors = []

    year, week_number, week_day = date.today().isocalendar()
    schools_weekly_status_list = []
    updated_schools = []
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
                _('Row {0}: Missing data for required column(s) {1}').format(row_index, ', '.join(missing_fields)),
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

        try:
            school_data['geopoint'] = Point(x=float(data['lon']), y=float(data['lat']))

            if school_data['geopoint'] == Point(x=0, y=0):
                errors.append(_('Row {0}: Bad data provided for geopoint: zero point').format(row_index))
                continue
        except (TypeError, ValueError):
            errors.append(_('Row {0}: Bad data provided for geopoint').format(row_index))
            continue

        if 'educ_level' in data:
            school_data['education_level'] = data['educ_level']

        if not school:
            school = School.objects.filter(
                name=data['name'], distance__lte=(school_data['geopoint'], D(m=500)),
                education_level=school_data['education_level'],
            ).first()

        if school and school.id in updated_schools:
            warnings.append(_('Row {0}: Bad data provided for school identifier: duplicate entry').format(row_index))
            continue

        if 'admin1' in data:
            school_data['admin_1_name'] = data['admin1']
        if 'admin2' in data:
            school_data['admin_2_name'] = data['admin2']
        if 'admin3' in data:
            school_data['admin_3_name'] = data['admin3']
        if 'admin4' in data:
            school_data['admin_4_name'] = data['admin4']

        school_data['name'] = data['name']

        # static data
        if 'environment' in data:
            if data['environment'] not in dict(School.ENVIRONMENT_STATUSES).keys():
                errors.append(
                    _('Row {0}: Bad data provided for environment: should be in {1}').format(
                        row_index, ', '.join(dict(School.ENVIRONMENT_STATUSES).keys()),
                    ),
                )
                continue
            school_data['environment'] = data['environment']
        if 'address' in data:
            school_data['address'] = data['address']
        if 'type_school' in data:
            school_data['school_type'] = data['type_school']

        # historical data
        if 'num_students' in data:
            if data['num_students'] < 0:
                errors.append(_('Row {0}: Bad data provided for num_students').format(row_index))
                continue
            history_data['num_students'] = sanitize_separators(data['num_students'])
        if 'num_teachers' in data:
            if data['num_teachers'] < 0:
                errors.append(_('Row {0}: Bad data provided for num_teachers').format(row_index))
                continue
            history_data['num_teachers'] = sanitize_separators(data['num_teachers'])
        if 'num_classroom' in data:
            if data['num_classroom'] < 0:
                errors.append(_('Row {0}: Bad data provided for num_classroom').format(row_index))
                continue
            history_data['num_classroom'] = sanitize_separators(data['num_classroom'])
        if 'num_latrines' in data:
            if data['num_latrines'] < 0:
                errors.append(_('Row {0}: Bad data provided for num_latrines').format(row_index))
                continue
            history_data['num_latrines'] = sanitize_separators(data['num_latrines'])

        if 'electricity' in data:
            history_data['electricity_availability'] = data['electricity'].lower() in ['true', 'yes', '1']

        if 'computer_lab' in data:
            history_data['computer_lab'] = data['computer_lab'].lower() in ['true', 'yes', '1']
        if 'num_computers' in data:
            if data['num_computers'] < 0:
                errors.append(_('Row {0}: Bad data provided for num_computers').format(row_index))
                continue
            history_data['num_computers'] = sanitize_separators(data['num_computers'])
            history_data['computer_lab'] = True

        if 'connectivity' in data:
            history_data['connectivity'] = data['connectivity'].lower() in ['true', 'yes', '1']
        if 'type_connectivity' in data:
            history_data['connectivity_type'] = data['type_connectivity']
        if 'speed_connectivity' in data:
            try:
                history_data['connectivity_speed'] = float(data['speed_connectivity'])
            except ValueError:
                errors.append(_('Row {0}: Bad data provided for connectivity_speed').format(row_index))
                continue
            history_data['connectivity'] = True
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

        schools_weekly_status_list.append(
            SchoolWeeklyStatus(
                year=year, week=week_number, school=school,
                date=date.today(), **history_data,
            ),
        )
        updated_schools.append(school.id)

        if i > 0 and i % 5000 == 0:
            SchoolWeeklyStatus.objects.filter(school_id__in=updated_schools, year=year, week=week_number).delete()
            SchoolWeeklyStatus.objects.bulk_create(schools_weekly_status_list)
            schools_weekly_status_list = []
            updated_schools = []

    if len(schools_weekly_status_list) > 0:
        SchoolWeeklyStatus.objects.filter(school_id__in=updated_schools, year=year, week=week_number).delete()
        SchoolWeeklyStatus.objects.bulk_create(schools_weekly_status_list)

    return warnings, errors
