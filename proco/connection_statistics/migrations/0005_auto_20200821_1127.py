# Generated by Django 2.2.15 on 2020-08-21 11:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('connection_statistics', '0004_auto_20200819_1323'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='countrydailystatus',
            options={'ordering': ('id',), 'verbose_name': 'Country Daily Status', 'verbose_name_plural': 'Country Daily Connectivity Summary'},
        ),
        migrations.AlterModelOptions(
            name='countryweeklystatus',
            options={'ordering': ('id',), 'verbose_name': 'Country Weekly Status', 'verbose_name_plural': 'Country Summary'},
        ),
        migrations.AlterModelOptions(
            name='realtimeconnectivity',
            options={'ordering': ('id',), 'verbose_name': 'Real Time Connectivity', 'verbose_name_plural': 'Real Time Connectivity Data'},
        ),
        migrations.AlterModelOptions(
            name='schooldailystatus',
            options={'ordering': ('id',), 'verbose_name': 'School Daily Status', 'verbose_name_plural': 'School Daily Connectivity Summary'},
        ),
        migrations.AlterModelOptions(
            name='schoolweeklystatus',
            options={'ordering': ('id',), 'verbose_name': 'School Weekly Status', 'verbose_name_plural': 'School Summary'},
        ),
    ]
