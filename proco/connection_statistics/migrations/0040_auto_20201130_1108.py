# Generated by Django 2.2.15 on 2020-11-30 11:08

from django.db import migrations, models


def update_countries_statuses(apps, schema_editor):
    Country = apps.get_model('locations', 'Country')

    for country in Country.objects.all():
        status_change_scheme = {
            1: 3,
            2: 4,
            3: 5,
        }

        if country.data_source and country.data_source.lower() == 'osm':
            country.last_weekly_status.integration_status = 1
            country.last_weekly_status.save(update_fields=('integration_status',))
            continue

        if country.last_weekly_status:
            if new_status := status_change_scheme.get(country.last_weekly_status.integration_status):
                country.last_weekly_status.integration_status = new_status
                country.last_weekly_status.save(update_fields=('integration_status',))


class Migration(migrations.Migration):

    dependencies = [
        ('connection_statistics', '0039_auto_20201120_1411'),
        ('locations', '0010_auto_20201120_1407'),
    ]

    operations = [
        migrations.AlterField(
            model_name='countryweeklystatus',
            name='integration_status',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Default Country Status'), (1, 'School OSM locations mapped'), (2, 'Country Joined Project Connect'), (3, 'School locations mapped'), (4, 'Static connectivity mapped'), (5, 'Real time connectivity mapped')], default=0),
        ),
        migrations.RunPython(update_countries_statuses, migrations.RunPython.noop),
    ]
