import logging

from django.utils import timezone

from proco.connection_statistics.models import RealTimeConnectivity
from proco.realtime_unicef.models import Measurement
from proco.schools.models import School
from proco.taskapp import app

logger = logging.getLogger('django.' + __name__)


@app.task
def sync_realtime_data():
    measurements = Measurement.objects.filter(timestamp__gt=Measurement.get_last_measurement_date())

    schools_ids = set((m.school_id for m in measurements))
    schools = {
        school.external_id: school
        for school in School.objects.filter(external_id__in=schools_ids)
    }

    realtime = []

    for measurement in measurements:
        if measurement.school_id not in schools:
            logger.debug(f'skipping measurement {measurement.uuid}: unknown school {measurement.school_id}')
            continue

        realtime.append(RealTimeConnectivity(
            created=measurement.timestamp,
            connectivity_speed=measurement.download,
            connectivity_latency=measurement.latency,
            school=schools[measurement.school_id],
        ))

    RealTimeConnectivity.objects.bulk_create(realtime)

    # not using aggregate because there can be new entries between two operations
    if measurements:
        last_update = max((m.timestamp for m in measurements))
    else:
        last_update = timezone.now()
    Measurement.set_last_measurement_date(last_update)
