# Generated by Django 2.2.16 on 2020-09-09 09:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('connection_statistics', '0009_auto_20200903_0830'),
    ]

    operations = [
        migrations.RenameField(
            model_name='schoolweeklystatus',
            old_name='connectivity_status',
            new_name='connectivity_type',
        ),
    ]
