import logging
from typing import Iterable, List, Tuple

from proco.locations.models import Country
from proco.schools.loaders import csv as csv_loader
from proco.schools.loaders import xls as xls_loader
from proco.schools.loaders.pipeline import (
    create_new_schools,
    delete_schools_not_in_bounds,
    get_validated_rows,
    map_schools_by_external_id,
    map_schools_by_geopoint,
    map_schools_by_name,
    remove_too_close_points,
    update_existing_schools,
    update_schools_weekly_statuses,
)

logger = logging.getLogger('django.' + __name__)


class UnsupportedFileFormatException(Exception):
    pass


def load_data(uploaded_file):
    if uploaded_file.name.endswith('.csv'):
        loader = csv_loader
    elif uploaded_file.name.endswith('.xls'):
        loader = xls_loader
    elif uploaded_file.name.endswith('.xlsx'):
        loader = xls_loader
    else:
        raise UnsupportedFileFormatException('Unsupported file format')

    return loader.load_file(uploaded_file)


def save_data(country: Country, loaded: Iterable[dict], ignore_errors=False) -> Tuple[List[str], List[str]]:
    schools_data, errors, warnings = get_validated_rows(country, loaded)
    if errors and not ignore_errors:
        return warnings, errors, 0

    map_schools_by_external_id(country, schools_data)
    map_schools_by_name(country, schools_data)
    map_schools_by_geopoint(country, schools_data)

    new_errors = remove_too_close_points(country, schools_data)
    errors.extend(new_errors)
    if errors and not ignore_errors:
        return warnings, errors, 0

    create_new_schools(schools_data)
    update_existing_schools(schools_data)

    new_errors = delete_schools_not_in_bounds(country, schools_data)
    errors.extend(new_errors)
    if errors and not ignore_errors:
        return warnings, errors, 0

    processed_rows = update_schools_weekly_statuses(schools_data)

    country.invalidate_country_related_cache()

    return warnings, errors, processed_rows
