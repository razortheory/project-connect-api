import traceback
from collections import Counter
from random import randint  # noqa

from django.contrib.gis.geos import MultiPoint, Point
from django.core.cache import cache
from django.db import transaction

from proco.connection_statistics.utils import update_country_weekly_status
from proco.locations.models import Country
from proco.schools.loaders import ingest
from proco.schools.loaders.ingest import load_data
from proco.schools.models import FileImport
from proco.taskapp import app


class FailedImportError(Exception):
    pass


def _find_country(loaded) -> [Country]:
    points = MultiPoint()
    loaded = list(loaded)

    maximum_points_threshold = 2000
    if len(loaded) > maximum_points_threshold:
        loaded = [loaded[randint(0, len(loaded) - 1)] for _i in range(maximum_points_threshold)]  # noqa

    for _i, data in enumerate(loaded):
        try:
            point = Point(x=float(data['lon']), y=float(data['lat']))

            if point == Point(x=0, y=0):
                continue
            else:
                points.append(point)
        except (TypeError, ValueError):
            continue

    countries = list(Country.objects.filter(geometry__intersects=points))

    if not countries:
        return None
    elif len(countries) == 1:
        return countries[0]
    else:
        countries_counter = Counter()
        for country in countries:
            instersections = country.geometry.intersection(points)
            if isinstance(instersections, Point):
                countries_counter[country] = 1
            else:
                countries_counter[country] = len(instersections)
        return countries_counter.most_common()[0][0]


@app.task(soft_time_limit=30 * 60, time_limit=30 * 60)
def process_loaded_file(pk: int, force: bool = False):
    imported_file = FileImport.objects.filter(pk=pk).first()
    if not imported_file:
        return

    imported_file.status = FileImport.STATUSES.started
    imported_file.save()

    try:
        imported_file.country = _find_country(load_data(imported_file.uploaded_file))
        if not imported_file.country:
            imported_file.status = FileImport.STATUSES.failed
            imported_file.errors = 'Error: Country not found'
            imported_file.save()
            return

        try:
            with transaction.atomic():
                warnings, errors = ingest.save_data(
                    imported_file.country, load_data(imported_file.uploaded_file), ignore_errors=force,
                )
                if errors and not force:
                    raise FailedImportError
        except FailedImportError:
            pass

        imported_file.errors = '\n'.join(errors)
        if warnings:
            imported_file.errors += '\nWarnings:\n'
            imported_file.errors += '\n'.join(map(str, warnings))

        if errors and not force:
            imported_file.status = FileImport.STATUSES.failed
        elif errors and force:
            imported_file.status = FileImport.STATUSES.completed_with_errors
        else:
            imported_file.status = FileImport.STATUSES.completed

        imported_file.save()

        if not errors or force:
            def update_stats():
                update_country_weekly_status(imported_file.country)
                cache.clear()

            transaction.on_commit(update_stats)
    except Exception:
        imported_file.status = FileImport.STATUSES.failed
        imported_file.errors = traceback.format_exc()
        imported_file.save()
        raise
