import traceback

from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

from proco.connection_statistics.models import SchoolWeeklyStatus
from proco.connection_statistics.utils import update_specific_country_weekly_status
from proco.locations.models import Country
from proco.schools.loaders import ingest
from proco.schools.models import FileImport
from proco.taskapp import app


class FailedImportError(Exception):
    pass


@app.task(soft_time_limit=30 * 60, time_limit=30 * 60)
def process_loaded_file(pk: int, force: bool=False):
    imported_file = FileImport.objects.filter(pk=pk).first()
    if not imported_file:
        return

    imported_file.status = FileImport.STATUSES.started
    imported_file.save()
    begin_time = timezone.now()

    try:
        # todo: rewrite with transaction savepoint
        try:
            with transaction.atomic():
                warnings, errors = ingest.save_data(imported_file.uploaded_file, force=force)
                if errors:
                    raise FailedImportError
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

        imported_file.save()

        if not errors:
            def update_stats():
                # TODO: update country status
                countries = SchoolWeeklyStatus.objects.filter(
                    created__gt=begin_time,
                ).order_by('school__country_id').values_list('school__country_id').distinct()
                countries = Country.objects.filter(id__in=countries)
                for country in countries:
                    update_specific_country_weekly_status(country)
                cache.clear()

            transaction.on_commit(update_stats)
    except Exception:
        imported_file.status = FileImport.STATUSES.failed
        imported_file.errors = traceback.format_exc()
        imported_file.save()
        raise
