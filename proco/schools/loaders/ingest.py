from datetime import date
from re import findall
from typing import Dict, Iterable, List, Tuple

from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.utils.translation import ugettext_lazy as _

from proco.connection_statistics.models import SchoolWeeklyStatus
from proco.locations.models import Country
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


def clean_number(num: [int, str]):
    if isinstance(num, str):
        num = ''.join(findall(r'[0-9]+', num))
    return num


def save_data(country: Country, loaded: Iterable[Dict]) -> Tuple[List[str], List[str]]:
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
            'country': country,
        }
        history_data = {}

        if 'school_id' in data:
            if len(data['school_id']) > (field_max_length := School._meta.get_field('external_id').max_length):
                errors.append(_(
                    'Row {0}: Bad data provided for school identifier: max length of {1} characters exceeded',
                ).format(row_index, field_max_length))
                continue
            school = School.objects.filter(external_id=data['school_id']).first()
            school_data['external_id'] = data['school_id']

        try:
            school_data['geopoint'] = Point(x=float(data['lon']), y=float(data['lat']))

            if school_data['geopoint'] == Point(x=0, y=0):
                errors.append(_('Row {0}: Bad data provided for geopoint: zero point').format(row_index))
                continue
            elif not country.geometry.contains(school_data['geopoint']):
                errors.append(_('Row {0}: Bad data provided for geopoint: point outside country').format(row_index))
                continue
        except (TypeError, ValueError):
            errors.append(_('Row {0}: Bad data provided for geopoint').format(row_index))
            continue

        if 'educ_level' in data:
            if len(data['educ_level']) > (field_max_length := School._meta.get_field('education_level').max_length):
                errors.append(
                    _('Row {0}: Bad data provided for name: max length of {1} characters exceeded').format(
                        row_index, field_max_length,
                    ))
                continue
            school_data['education_level'] = data['educ_level']

        if 'name' in data:
            if len(data['name']) > (field_max_length := School._meta.get_field('name').max_length):
                errors.append(
                    _('Row {0}: Bad data provided for name: max length of {1} characters exceeded').format(
                        row_index, field_max_length,
                    ))
                continue

        if not school:
            school_qs = School.objects.filter(
                name=data['name'], geopoint__distance_lte=(school_data['geopoint'], D(m=500)),
            )
            if school_data.get('education_level'):
                school_qs = school_qs.filter(education_level=school_data['education_level'])
            school = school_qs.first()

        if school and school.id in updated_schools:
            warnings.append(_('Row {0}: Bad data provided for school identifier: duplicate entry').format(row_index))
            continue

        admin_name_max_length = School._meta.get_field('admin1').max_length
        if 'admin1' in data:
            if len(data['admin1']) > admin_name_max_length:
                errors.append(
                    _('Row {0}: Bad data provided for admin1: max length of {1} characters exceeded').format(
                        row_index, admin_name_max_length,
                    ))
                continue
            school_data['admin_1_name'] = data['admin1']
        if 'admin2' in data:
            if len(data['admin2']) > admin_name_max_length:
                errors.append(
                    _('Row {0}: Bad data provided for admin2: max length of {1} characters exceeded').format(
                        row_index, admin_name_max_length,
                    ))
                continue
            school_data['admin_2_name'] = data['admin2']
        if 'admin3' in data:
            if len(data['admin3']) > admin_name_max_length:
                errors.append(
                    _('Row {0}: Bad data provided for admin3: max length of {1} characters exceeded').format(
                        row_index, admin_name_max_length,
                    ))
                continue
            school_data['admin_3_name'] = data['admin3']
        if 'admin4' in data:
            if len(data['admin4']) > admin_name_max_length:
                errors.append(
                    _('Row {0}: Bad data provided for admin4: max length of {1} characters exceeded').format(
                        row_index, admin_name_max_length,
                    ))
                continue
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
            if len(data['environment']) > (field_max_length := School._meta.get_field('environment').max_length):
                errors.append(
                    _('Row {0}: Bad data provided for environment: max length of {1} characters exceeded').format(
                        row_index, field_max_length,
                    ))
                continue
            school_data['environment'] = data['environment']
        if 'address' in data:
            if len(data['address']) > (field_max_length := School._meta.get_field('address').max_length):
                errors.append(
                    _('Row {0}: Bad data provided for address: max length of {1} characters exceeded').format(
                        row_index, field_max_length,
                    ))
                continue
            school_data['address'] = data['address']
        if 'type_school' in data:
            if len(data['type_school']) > (field_max_length := School._meta.get_field('school_type').max_length):
                errors.append(
                    _('Row {0}: Bad data provided for type_school: max length of {1} characters exceeded').format(
                        row_index, field_max_length,
                    ))
                continue
            school_data['school_type'] = data['type_school']

        # historical data
        if 'num_students' in data:
            try:
                data['num_students'] = int(data['num_students'])
            except ValueError:
                errors.append(_('Row {0}: Bad data provided for num_students').format(row_index))
                continue

            if data['num_students'] < 0:
                errors.append(_('Row {0}: Bad data provided for num_students').format(row_index))
                continue
            history_data['num_students'] = clean_number(data['num_students'])
        if 'num_teachers' in data:
            try:
                data['num_teachers'] = int(data['num_teachers'])
            except ValueError:
                errors.append(_('Row {0}: Bad data provided for num_teachers').format(row_index))
                continue

            if data['num_teachers'] < 0:
                errors.append(_('Row {0}: Bad data provided for num_teachers').format(row_index))
                continue
            history_data['num_teachers'] = clean_number(data['num_teachers'])
        if 'num_classroom' in data:
            try:
                data['num_classroom'] = int(data['num_classroom'])
            except ValueError:
                errors.append(_('Row {0}: Bad data provided for num_classroom').format(row_index))
                continue

            if data['num_classroom'] < 0:
                errors.append(_('Row {0}: Bad data provided for num_classroom').format(row_index))
                continue
            history_data['num_classroom'] = clean_number(data['num_classroom'])
        if 'num_latrines' in data:
            try:
                data['num_latrines'] = int(data['num_latrines'])
            except ValueError:
                errors.append(_('Row {0}: Bad data provided for num_latrines').format(row_index))
                continue

            if data['num_latrines'] < 0:
                errors.append(_('Row {0}: Bad data provided for num_latrines').format(row_index))
                continue
            history_data['num_latrines'] = clean_number(data['num_latrines'])

        if 'electricity' in data:
            history_data['electricity_availability'] = data['electricity'].lower() in ['true', 'yes', '1']

        if 'computer_lab' in data:
            history_data['computer_lab'] = data['computer_lab'].lower() in ['true', 'yes', '1']
        if 'num_computers' in data:
            try:
                data['num_computers'] = int(data['num_computers'])
            except ValueError:
                errors.append(_('Row {0}: Bad data provided for num_computers').format(row_index))
                continue

            if data['num_computers'] < 0:
                errors.append(_('Row {0}: Bad data provided for num_computers').format(row_index))
                continue
            history_data['num_computers'] = clean_number(data['num_computers'])
            history_data['computer_lab'] = True

        if 'connectivity' in data:
            history_data['connectivity'] = data['connectivity'].lower() in ['true', 'yes', '1']
        if 'type_connectivity' in data:
            if len(data['type_connectivity']) > (
                field_max_length := SchoolWeeklyStatus._meta.get_field('connectivity_type').max_length
            ):
                errors.append(
                    _('Row {0}: Bad data provided for type_connectivity: max length of {1} characters exceeded').format(
                        row_index, field_max_length,
                    ))
                continue
            history_data['connectivity_type'] = data['type_connectivity']
        if 'speed_connectivity' in data:
            try:
                speed = float(data['speed_connectivity'])
                if 600 > speed > 500:
                    speed = 0.5
                history_data['connectivity_speed'] = speed * (10 ** 6)  # mbps to bps
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

        status = SchoolWeeklyStatus(year=year, week=week_number, school=school, **history_data)
        status.date = status.get_date()
        status.connectivity_status = status.get_connectivity_status()

        schools_weekly_status_list.append(status)
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
