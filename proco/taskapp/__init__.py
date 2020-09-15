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
    'aggregate_real_time_data': {
        'task': 'proco.connection_statistics.aggregate_real_time_data',
        'schedule': crontab(hour='*/6', minute=0),
        'args': (),
    },
    'aggregate_daily_statistics': {
        'task': 'proco.connection_statistics.aggregate_daily_statistics',
        'schedule': crontab(hour=0, minute=0),
        'args': (),
    },
    'load_brasil_daily_statistics': {
        'task': 'proco.connection_statistics.load_brasil_daily_statistics',
        'schedule': crontab(hour='*/6', minute=0),
        'args': (),
    },
}
app.conf.timezone = 'UTC'
