# Generated by Django 2.2.16 on 2020-10-12 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('connection_statistics', '0027_auto_20201007_0849'),
    ]

    operations = [
        migrations.AlterField(
            model_name='countryweeklystatus',
            name='avg_distance_school',
            field=models.FloatField(blank=True, default=None, null=True),
        ),
    ]