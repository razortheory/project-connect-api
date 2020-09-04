# Generated by Django 2.2.15 on 2020-09-03 08:30

import datetime
import itertools

from django.db import migrations, models
from django.utils.timezone import utc


def fill_date(apps, schema_editor):
    CountryWeeklyStatus = apps.get_model('connection_statistics', 'CountryWeeklyStatus')
    SchoolWeeklyStatus = apps.get_model('connection_statistics', 'SchoolWeeklyStatus')
    for obj in itertools.chain(CountryWeeklyStatus.objects.all(), SchoolWeeklyStatus.objects.all()):
        obj.date = datetime.datetime.strptime(f'{obj.year}-W{obj.week}-1', "%Y-W%W-%w")


class Migration(migrations.Migration):
    dependencies = [
        ('connection_statistics', '0008_auto_20200903_0743'),
    ]

    operations = [
        migrations.AddField(
            model_name='countryweeklystatus',
            name='date',
            field=models.DateField(default=datetime.datetime(2020, 9, 3, 8, 30, 30, 315764, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='schoolweeklystatus',
            name='date',
            field=models.DateField(default=datetime.datetime(2020, 9, 3, 8, 30, 34, 100522, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.RunPython(fill_date, migrations.RunPython.noop),
    ]
