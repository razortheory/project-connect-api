import logging
from datetime import date
from typing import Iterable, List, Tuple

from django.db.models import F
from django.utils.translation import ugettext_lazy as _

from scipy.spatial import KDTree

from proco.connection_statistics.models import SchoolWeeklyStatus
from proco.locations.models import Country
from proco.schools.loaders.validation import validate_point_distance, validate_row
from proco.schools.models import School
from proco.utils.geometry import cartesian

logger = logging.getLogger('django.' + __name__)


def get_validated_rows(country: Country, loaded: Iterable[dict]) -> Tuple[List[dict], List[str], List[str]]:
    errors = []
    warnings = []
    csv_external_ids = []
    csv_names = []
    rows = []

    for i, data in enumerate(loaded):
        row_index = i + 2  # enumerate starts from zero plus header
        # remove non-unicode symbols from keys and empty suffixes/prefixes
        data = {
            key.encode('ascii', 'ignore').decode(): value.strip()
            for key, value in data.items()
        }
        # remove empty strings from data
        # empty values check is ugly; should be refactored (like validation in overall, it has lot of duplicated code)
        data = {
            key: value
            for key, value in data.items()
            if value != '' and ((not key.startswith('admin') and value not in ['na', 'nd']) or key.startswith('admin'))
        }
        if not data:
            continue

        if i % 1000 == 0:
            logger.info(f'validated {i}')

        school_data, history_data, row_errors, row_warnings = validate_row(country, data)
        if row_errors:
            errors.extend(f'Row {row_index}: {error}' for error in row_errors)
            continue

        if row_warnings:
            warnings.extend(f'Row {row_index}: {warning}' for warning in row_warnings)
            continue

        if 'external_id' in school_data:
            if school_data['external_id'].lower() in csv_external_ids:
                warnings.append(_('Bad data provided for school identifier: duplicate entry'))
                continue
            csv_external_ids.append(school_data['external_id'].lower())

        if 'name' in school_data:
            if school_data['name'].lower() in csv_names:
                warnings.append(_('Bad data provided for school name: duplicate entry'))
                continue
            csv_names.append(school_data['name'].lower())

        rows.append({
            'row_index': row_index,
            'school_data': school_data,
            'history_data': history_data,
        })

    return rows, errors, warnings


def map_schools_by_external_id(country: Country, rows: List[dict]):
    # search by external id
    schools_with_external_id = {
        data['school_data']['external_id'].lower(): data
        for data in rows
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
                schools_with_external_id[school.external_id]['school'] = school


def map_schools_by_name(country: Country, rows: List[dict]):
    # search by name
    schools_with_name = {
        data['school_data']['name'].lower(): data
        for data in rows
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
                schools_with_name[school.name_lower]['school'] = school


def remove_too_close_points(country: Country, rows: List[dict]) -> List[str]:
    # 1. get all possible points from schools table
    # 2. for every changed point, remove it from list and re-check it still valid
    # 3. for every new point, check it's distance from schools of similar type is greater than 500m
    # P.S. second step missing, kd-trees don't allow insertions.
    # solutions: don't allow point to be removed. pros: we can skip bad geopoint if school exists

    errors = []
    school_points = {'all': []}

    for school in School.objects.filter(country=country).values('education_level', 'geopoint'):
        if school['education_level'] not in school_points:
            school_points[school['education_level']] = []
        cartesian_coord = cartesian(school['geopoint'].y, school['geopoint'].x)
        school_points[school['education_level']].append(cartesian_coord)
        school_points['all'].append(cartesian_coord)

    # add all points to generate final kdtree
    for data in [d for d in rows if 'school' not in d]:
        point = data['school_data']['geopoint']
        cartesian_coord = cartesian(point.y, point.x)
        education_level = data['school_data'].get('education_level')
        if education_level:
            if education_level not in school_points:
                school_points[education_level] = []
            school_points[education_level].append(cartesian_coord)
        school_points['all'].append(cartesian_coord)

    for key in school_points.keys():
        school_points[key] = KDTree(school_points[key])

    new_schools = [d for d in rows if 'school' not in d]

    logger.info(f'started points check, {len(rows)} items')

    bad_schools = []
    for i, data in enumerate(new_schools):
        point = data['school_data']['geopoint']
        cartesian_coord = cartesian(point.y, point.x)
        education_level = data['school_data'].get('education_level')

        if i % 1000 == 0:
            logger.info(f'processed {i} geopoints')

        if education_level:
            if not validate_point_distance(school_points[education_level], cartesian_coord):
                errors.append(_(
                    'Row {0}: Geopoint is closer than 500m to another with same education level.',
                ).format(data['row_index']))
                bad_schools.append(data)
        else:
            if not validate_point_distance(school_points['all'], cartesian_coord):
                errors.append(_(
                    'Row {0}: Geopoint is closer than 500m to another. '
                    'Please specify education_level for better search.',
                ).format(data['row_index']))
                bad_schools.append(data)

    for bad_data in bad_schools:
        rows.remove(bad_data)

    logger.info(f'finished points check, {len(rows)} items left')

    return errors


def create_new_schools(rows: List[dict]):
    # bulk create new schools
    new_schools = []
    for data in rows:
        if 'school' in data:
            continue

        school = School(**data['school_data'])
        school.name_lower = school.name.lower()
        school.external_id = school.external_id.lower()

        new_schools.append(school)
        data['school'] = school
        data['school_created'] = True

    if new_schools:
        logger.info(f'{len(new_schools)} schools will be created')
        School.objects.bulk_create(new_schools, batch_size=1000)


def update_existing_schools(rows: List[dict]):
    # bulk update existing ones
    all_schools_to_update = [data for data in rows if not data.get('school_created', False)]
    logger.info(f'{len(all_schools_to_update)} schools will be updated')
    fields_combinations = {tuple(sorted(data['school_data'].keys())) for data in all_schools_to_update}
    for fields_combination in fields_combinations:
        schools_to_update = [
            data['school']
            for data in all_schools_to_update
            if tuple(sorted(data['school_data'].keys())) == fields_combination
        ]
        logger.info(f'{len(schools_to_update)} schools will be updated with {fields_combination}')
        School.objects.bulk_update(schools_to_update, fields_combination, batch_size=1000)


def delete_schools_not_in_bounds(country: Country, rows: List[dict]) -> List[str]:
    errors = []

    # check & remove schools not in bounds. this is the fastest way
    School.objects.filter(country=country).exclude(geopoint__within=F('country__geometry')).delete()
    logger.info(f'{len(rows)} schools before filtering')

    schools_within = School.objects.filter(id__in=[d['school'].id for d in rows]).values_list('id', flat=True)
    bad_rows = []
    for data in rows:
        if data['school'].id not in schools_within:
            errors.append(_('Row {0}: Bad data provided for geopoint: point outside country').format(data['row_index']))
            bad_rows.append(data)

    for bad_row in bad_rows:
        rows.remove(bad_row)

    return errors


def update_schools_weekly_statuses(rows: List[dict]):
    year, week_number, week_day = date.today().isocalendar()
    schools_weekly_status_list = []
    updated_schools = {}

    # prepare new values for weekly statuses
    for data in rows:
        school = data['school']
        history_data = data['history_data']

        status = SchoolWeeklyStatus.objects.filter(school=school).last()
        if status:
            status.id = None
            for k, v in history_data.items():
                setattr(status, k, v)
        else:
            status = SchoolWeeklyStatus(school=school, **history_data)

        status.year = year
        status.week = week_number
        status.date = status.get_date()

        schools_weekly_status_list.append(status)
        updated_schools[school.id] = school

    # re-create weekly statuses with new data
    if schools_weekly_status_list:
        SchoolWeeklyStatus.objects.filter(school_id__in=updated_schools.keys(), year=year, week=week_number).delete()
        SchoolWeeklyStatus.objects.bulk_create(schools_weekly_status_list, batch_size=1000)

        # set last weekly id to correct one; signals don't work when batch performed
        for status in schools_weekly_status_list:
            updated_schools[status.school_id].last_weekly_status = status
        School.objects.bulk_update(updated_schools.values(), ['last_weekly_status'], batch_size=1000)

        logger.info(f'updated weekly statuses for {len(schools_weekly_status_list)} schools')
