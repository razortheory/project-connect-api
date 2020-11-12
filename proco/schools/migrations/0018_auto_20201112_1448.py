# Generated by Django 2.2.15 on 2020-11-12 14:48

import re
from django.db import migrations


def fill_data_source(apps, schema_editor):
    FileImport = apps.get_model('schools', 'FileImport')

    for file in FileImport.objects.filter(country__isnull=False):
        source = re.search(r'\d+-(.*)-\d+', file.uploaded_file.name.split('/')[-1]).group(1)
        pretty_source = source.replace('_', ' ')
        file.country.data_source = pretty_source
        file.country.save()


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0017_auto_20201103_1415'),
    ]

    operations = [
        migrations.RunPython(fill_data_source, migrations.RunPython.noop),
    ]
