# Generated by Django 2.2.15 on 2020-11-19 20:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('connection_statistics', '0035_auto_20201119_1942'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='schoolweeklystatus',
            name='connectivity_status',
        ),
    ]