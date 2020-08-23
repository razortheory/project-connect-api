# Generated by Django 2.2.15 on 2020-08-22 09:19

import os
import uuid

from django.conf import settings
from django.core.files import File
from django.db import migrations


def get_random_name_image(filename):
    extension = os.path.splitext(filename)[1]
    return f'{settings.IMAGES_PATH}/{uuid.uuid4()}{extension}'


def fill_flags(apps, schema_editor):
    Country = apps.get_model("locations", "Country")

    for country in Country.objects.all().order_by('id'):
        try:
            filename = 'proco/locations/migrations/flags/{}.svg'.format(country.id)
            flag = open(filename, 'rb')
            country.flag.save(get_random_name_image(filename), File(flag), save=True)
            country.save()
        except FileNotFoundError as e:
            print (e)
            print ("Flag for {} not found".format(country))


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0003_auto_20200817_1005'),
    ]

    operations = [
        migrations.RunPython(fill_flags, migrations.RunPython.noop),
    ]
