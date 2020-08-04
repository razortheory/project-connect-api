from celery.schedules import timedelta
from celery.task import periodic_task


@periodic_task(run_every=timedelta(seconds=10))
def test_task():
    print('Celery works.')
