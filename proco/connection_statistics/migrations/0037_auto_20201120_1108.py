# Generated by Django 2.2.15 on 2020-11-20 11:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('connection_statistics', '0036_remove_schoolweeklystatus_connectivity_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='countryweeklystatus',
            name='connectivity_availability',
        ),
        migrations.RemoveField(
            model_name='countryweeklystatus',
            name='coverage_availability',
        ),
    ]
