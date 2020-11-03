from datetime import date
from re import findall
from typing import Dict, Iterable, List, Tuple

from django.contrib.gis.geos import Point
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


external_id_max_length = School._meta.get_field('external_id').max_length
education_level_max_length = School._meta.get_field('education_level').max_length
name_max_length = School._meta.get_field('name').max_length
admin_1_name_max_length = School._meta.get_field('admin_1_name').max_length
environment_max_length = School._meta.get_field('environment').max_length
address_max_length = School._meta.get_field('address').max_length
school_type_max_length = School._meta.get_field('school_type').max_length
admin_name_max_length = School._meta.get_field('admin_1_name').max_length
environment_values = dict(School.ENVIRONMENT_STATUSES).keys()
required_fields = {'name', 'lat', 'lon'}


# todo: get rid of row_index, we don't need it inside
def validate_school_data(row_index: int, country: Country, data: dict):
    errors = []
    warnings = []

    missing_fields = required_fields.difference(set(data.keys()))
    if missing_fields:
        errors.append(
            _('Row {0}: Missing data for required column(s) {1}').format(row_index, ', '.join(missing_fields)),
        )
        return None, None, errors, warnings

    school_data = {
        'country': country,
    }
    history_data = {}

    if 'school_id' in data:
        if len(data['school_id']) > external_id_max_length:
            errors.append(_(
                'Row {0}: Bad data provided for school identifier: max length of {1} characters exceeded',
            ).format(row_index, external_id_max_length))
            return None, None, errors, warnings
        school_data['external_id'] = data['school_id'].lower()

    try:
        school_data['geopoint'] = Point(x=float(data['lon']), y=float(data['lat']))

        if school_data['geopoint'].x == 0 and school_data['geopoint'].y == 0:
            errors.append(_('Row {0}: Bad data provided for geopoint: zero point').format(row_index))
            return None, None, errors, warnings
        # todo: this is slow part (30s vs 0.5s commented)
        # todo: calculate simplified geometry INSIDE original. if not belong, use original
        # if geometry is simple (don't intersects) and have no holes, we can try to use maximum square first
        elif not country.geometry.contains(school_data['geopoint']):
            errors.append(_('Row {0}: Bad data provided for geopoint: point outside country').format(row_index))
            return None, None, errors, warnings
    except (TypeError, ValueError):
        errors.append(_('Row {0}: Bad data provided for geopoint').format(row_index))
        return None, None, errors, warnings

    if 'educ_level' in data:
        if len(data['educ_level']) > education_level_max_length:
            errors.append(
                _('Row {0}: Bad data provided for name: max length of {1} characters exceeded').format(
                    row_index, education_level_max_length,
                ))
            return None, None, errors, warnings
        school_data['education_level'] = data['educ_level']

    if 'name' in data:
        if len(data['name']) > name_max_length:
            errors.append(
                _('Row {0}: Bad data provided for name: max length of {1} characters exceeded').format(
                    row_index, name_max_length,
                ))
            return None, None, errors, warnings

    if 'admin1' in data:
        if len(data['admin1']) > admin_name_max_length:
            errors.append(
                _('Row {0}: Bad data provided for admin1: max length of {1} characters exceeded').format(
                    row_index, admin_name_max_length,
                ))
            return None, None, errors, warnings
        school_data['admin_1_name'] = data['admin1']
    if 'admin2' in data:
        if len(data['admin2']) > admin_name_max_length:
            errors.append(
                _('Row {0}: Bad data provided for admin2: max length of {1} characters exceeded').format(
                    row_index, admin_name_max_length,
                ))
            return None, None, errors, warnings
        school_data['admin_2_name'] = data['admin2']
    if 'admin3' in data:
        if len(data['admin3']) > admin_name_max_length:
            errors.append(
                _('Row {0}: Bad data provided for admin3: max length of {1} characters exceeded').format(
                    row_index, admin_name_max_length,
                ))
            return None, None, errors, warnings
        school_data['admin_3_name'] = data['admin3']
    if 'admin4' in data:
        if len(data['admin4']) > admin_name_max_length:
            errors.append(
                _('Row {0}: Bad data provided for admin4: max length of {1} characters exceeded').format(
                    row_index, admin_name_max_length,
                ))
            return None, None, errors, warnings
        school_data['admin_4_name'] = data['admin4']

    school_data['name'] = data['name']

    # static data
    if 'environment' in data:
        if data['environment'] not in environment_values:
            errors.append(
                _('Row {0}: Bad data provided for environment: should be in {1}').format(
                    row_index, ', '.join(environment_values),
                ),
            )
            return None, None, errors, warnings
        if len(data['environment']) > environment_max_length:
            errors.append(
                _('Row {0}: Bad data provided for environment: max length of {1} characters exceeded').format(
                    row_index, environment_max_length,
                ))
            return None, None, errors, warnings
        school_data['environment'] = data['environment']
    if 'address' in data:
        if len(data['address']) > address_max_length:
            errors.append(
                _('Row {0}: Bad data provided for address: max length of {1} characters exceeded').format(
                    row_index, address_max_length,
                ))
            return None, None, errors, warnings
        school_data['address'] = data['address']
    if 'type_school' in data:
        if len(data['type_school']) > school_type_max_length:
            errors.append(
                _('Row {0}: Bad data provided for type_school: max length of {1} characters exceeded').format(
                    row_index, school_type_max_length,
                ))
            return None, None, errors, warnings
        school_data['school_type'] = data['type_school']

    # historical data
    if 'num_students' in data:
        try:
            data['num_students'] = int(data['num_students'])
        except ValueError:
            errors.append(_('Row {0}: Bad data provided for num_students').format(row_index))
            return None, None, errors, warnings

        if data['num_students'] < 0:
            errors.append(_('Row {0}: Bad data provided for num_students').format(row_index))
            return None, None, errors, warnings
        history_data['num_students'] = clean_number(data['num_students'])
    if 'num_teachers' in data:
        try:
            data['num_teachers'] = int(data['num_teachers'])
        except ValueError:
            errors.append(_('Row {0}: Bad data provided for num_teachers').format(row_index))
            return None, None, errors, warnings

        if data['num_teachers'] < 0:
            errors.append(_('Row {0}: Bad data provided for num_teachers').format(row_index))
            return None, None, errors, warnings
        history_data['num_teachers'] = clean_number(data['num_teachers'])
    if 'num_classroom' in data:
        try:
            data['num_classroom'] = int(data['num_classroom'])
        except ValueError:
            errors.append(_('Row {0}: Bad data provided for num_classroom').format(row_index))
            return None, None, errors, warnings

        if data['num_classroom'] < 0:
            errors.append(_('Row {0}: Bad data provided for num_classroom').format(row_index))
            return None, None, errors, warnings
        history_data['num_classroom'] = clean_number(data['num_classroom'])
    if 'num_latrines' in data:
        try:
            data['num_latrines'] = int(data['num_latrines'])
        except ValueError:
            errors.append(_('Row {0}: Bad data provided for num_latrines').format(row_index))
            return None, None, errors, warnings

        if data['num_latrines'] < 0:
            errors.append(_('Row {0}: Bad data provided for num_latrines').format(row_index))
            return None, None, errors, warnings
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
            return None, None, errors, warnings

        if data['num_computers'] < 0:
            errors.append(_('Row {0}: Bad data provided for num_computers').format(row_index))
            return None, None, errors, warnings
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
            return None, None, errors, warnings
        history_data['connectivity_type'] = data['type_connectivity']
    if 'speed_connectivity' in data:
        try:
            speed = float(data['speed_connectivity'])
            if 600 > speed > 500:
                speed = 0.5
            history_data['connectivity_speed'] = speed * (10 ** 6)  # mbps to bps
        except ValueError:
            errors.append(_('Row {0}: Bad data provided for connectivity_speed').format(row_index))
            return None, None, errors, warnings
        history_data['connectivity'] = True
    if 'latency_connectivity' in data:
        history_data['connectivity_latency'] = data['latency_connectivity']

    if 'water' in data:
        history_data['running_water'] = data['water'].lower() in ['true', 'yes', '1']

    return school_data, history_data, errors, warnings


def save_data(country: Country, loaded: Iterable[Dict], ignore_errors=False) -> Tuple[List[str], List[str]]:
    warnings = []
    errors = []

    year, week_number, week_day = date.today().isocalendar()
    schools_weekly_status_list = []
    updated_schools = {}
    csv_external_ids = []
    csv_names = []

    schools_data = []

    for i, data in enumerate(loaded):
        row_index = i + 2  # enumerate starts from zero plus header
        # remove empty strings from data; ignore unicode from keys
        # empty values check is ugly; should be refactored (like validation in overall, it has lot of duplicated code)
        data = {
            key.encode('ascii', 'ignore').decode(): value
            for key, value in data.items()
            if value != '' and ((not key.startswith('admin') and value not in ['na', 'nd']) or key.startswith('admin'))
        }
        if not data:
            continue

        if i % 1000 == 0:
            print(f'validated {i}')

        school_data, history_data, row_errors, row_warnings = validate_school_data(row_index, country, data)
        if 'external_id' in school_data:
            if school_data['external_id'] in csv_external_ids:
                row_warnings.append(
                    _('Row {0}: Bad data provided for school identifier: duplicate entry').format(row_index))
            csv_external_ids.append(school_data['external_id'])

        if 'name' in school_data:
            if school_data['name'] in csv_names:
                row_warnings.append(
                    _('Row {0}: Bad data provided for school name: duplicate entry').format(row_index))
            csv_names.append(school_data['name'])

        if row_errors:
            errors.extend(row_errors)
            continue

        if row_warnings:
            warnings.extend(row_warnings)
            continue

        schools_data.append({
            'row_index': row_index,
            'school_data': school_data,
            'history_data': history_data,
        })

    print(f'validated data, {len(errors)} errors')

    if errors and not ignore_errors:
        return warnings, errors

    # search by external id
    schools_with_external_id = {
        data['school_data']['external_id'].lower(): data
        for data in schools_data
        if 'external_id' in data['school_data']
    }
    if schools_with_external_id:
        external_ids = list(schools_with_external_id.keys())
        for i in range(0, len(external_ids), 500):
            schools_by_external_id = School.objects.filter(
                country=country,
                external_id__in=external_ids[i:min(i + 500, len(external_ids))],
            )
            for school in schools_by_external_id:
                schools_with_external_id[school.external_id.lower()]['school'] = school

    # search by name
    schools_with_name = {
        data['school_data']['name'].lower(): data
        for data in schools_data
        if 'school' not in data
    }
    if schools_with_name:
        names = list(schools_with_name.keys())
        for i in range(0, len(names), 500):
            schools_by_name = School.objects.filter(
                country=country,
                name_lower__in=names[i:min(i + 500, len(names))],
            )
            for school in schools_by_name:
                schools_with_name[school.name.lower()]['school'] = school

    # post validations
    # check distance here
    # 1. get all possible points from schools table
    # 2. for every changed point, remove it from list and re-check it still valid
    # 3. for every new point, check it's distance from schools of similar type is greater than 500m

    # todo: we need validation, not fuzzy search
    # school_qs = School.objects.filter(
    #     name=data['name'], geopoint__distance_lte=(school_data['geopoint'], D(m=500)),
    # )
    # if school_data.get('education_level'):
    #     school_qs = school_qs.filter(education_level=school_data['education_level'])
    # school = school_qs.first()

    # bulk create new schools
    new_schools = []
    for data in [d for d in schools_data if 'school' not in d]:
        school = School(**data['school_data'])
        school.name_lower = school.name.lower()
        school.external_id = school.external_id.lower()

        new_schools.append(school)
        data['school'] = school
        data['school_created'] = True

    for i in range(0, len(new_schools), 1000):
        School.objects.bulk_create(new_schools[i:min(i + 1000, len(new_schools))])

    # bulk update existing ones
    all_schools_to_update = [data for data in schools_data if not data.get('school_created', False)]
    fields_combinations = {tuple(data['school_data'].keys()) for data in all_schools_to_update}
    for fields_combination in fields_combinations:
        schools_to_update = [
            data['school']
            for data in all_schools_to_update
            if tuple(data.keys()) == fields_combination
        ]
        School.objects.bulk_update(schools_to_update, fields_combination, batch_size=1000)

    # prepare new values for weekly statuses
    for data in schools_data:
        school = data['school']
        history_data = data['history_data']

        status = SchoolWeeklyStatus(year=year, week=week_number, school=school, **history_data)
        status.date = status.get_date()
        status.connectivity_status = status.get_connectivity_status()
        status.coverage_type, status.coverage_status = status.get_coverage_type_and_status()

        schools_weekly_status_list.append(status)
        updated_schools[school.id] = school

    # re-create weekly statuses with new data
    if schools_weekly_status_list:
        SchoolWeeklyStatus.objects.filter(school_id__in=updated_schools.keys(), year=year, week=week_number).delete()
        SchoolWeeklyStatus.objects.bulk_create(schools_weekly_status_list, batch_size=1000)

        # set last weekly id to correct one; signals don't work when batch performed
        for status in schools_weekly_status_list:
            updated_schools[status.school_id].last_weekly_status_id = status.id
        School.objects.bulk_update(updated_schools.values(), ['last_weekly_status_id'], batch_size=1000)

    return warnings, errors
