# Generated by Django 2.2.16 on 2020-11-03 14:13

from django.db import migrations
from django.db.models.functions import Lower


def fill_new_fields(apps, schema_editor):
    School = apps.get_model('schools', 'School')
    School.objects.update(external_id=Lower('external_id'), name_lower=Lower('name'))


class Migration(migrations.Migration):
    dependencies = [
        ('schools', '0015_school_name_lower'),
    ]

    operations = [
        migrations.RunPython(fill_new_fields, migrations.RunPython.noop),
    ]
