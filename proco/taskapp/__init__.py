import os

from django.conf import settings

from celery import Celery
from celery.schedules import crontab

if not settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')

app = Celery('proco')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.beat_schedule = {
    'update_real_time_data': {
        'task': 'proco.connection_statistics.update_real_time_data',
        # todo: we need to make more flexible system to update data for previous day
        'schedule': crontab(hour='6,12,18,22', minute=0),
        'args': (),
    },
    'update_brasil_schools': {
        'task': 'proco.connection_statistics.update_brasil_schools',
        'schedule': crontab(hour=1, minute=0),
        'args': (),
    },
}
app.conf.timezone = 'UTC'
