# Generated by Django 2.2.16 on 2020-09-30 07:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('connection_statistics', '0022_auto_20200929_1359'),
    ]

    operations = [
        migrations.AlterField(
            model_name='countrydailystatus',
            name='connectivity_speed',
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='realtimeconnectivity',
            name='connectivity_speed',
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='schooldailystatus',
            name='connectivity_speed',
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='schoolweeklystatus',
            name='connectivity_speed',
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
    ]