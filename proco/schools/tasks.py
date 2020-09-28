import traceback

from django.core.cache import cache
from django.db import transaction

from proco.connection_statistics.utils import update_specific_country_weekly_status
from proco.locations.models import Country
from proco.schools.loaders import ingest
from proco.schools.loaders.ingest import load_data
from proco.schools.models import FileImport
from proco.taskapp import app


class FailedImportError(Exception):
    pass


@app.task(soft_time_limit=30 * 60, time_limit=30 * 60)
def process_loaded_file(country_pk: int, pk: int):
    country = Country.objects.get(pk=country_pk)
    imported_file = FileImport.objects.filter(pk=pk).first()
    if not imported_file:
        return

    imported_file.status = FileImport.STATUSES.started
    imported_file.save()

    try:
        # todo: rewrite with transaction savepoint
        try:
            with transaction.atomic():
                warnings, errors = ingest.save_data(country, load_data(imported_file.uploaded_file))
                if errors:
                    raise FailedImportError
                else:
                    update_specific_country_weekly_status(country)
        except FailedImportError:
            pass

        imported_file.errors = '\n'.join(errors)
        if warnings:
            imported_file.errors += '\nWarnings:\n'
            imported_file.errors += '\n'.join(warnings)

        if errors:
            imported_file.status = FileImport.STATUSES.failed
        else:
            imported_file.status = FileImport.STATUSES.completed
            cache.clear()

        imported_file.save()
    except Exception:
        imported_file.status = FileImport.STATUSES.failed
        imported_file.errors = traceback.format_exc()
        imported_file.save()
        raise
