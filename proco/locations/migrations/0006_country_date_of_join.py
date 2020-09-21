# Generated by Django 2.2.16 on 2020-09-18 07:34

from django.db import migrations, models


def fill_date_of_join(apps, schema_editor):
    Country = apps.get_model("locations", "Country")
    CountryWeeklyStatus = apps.get_model("connection_statistics", "CountryWeeklyStatus")

    for country in Country.objects.filter(weekly_status__isnull=False):
        weekly_status = CountryWeeklyStatus.objects.filter(country=country).order_by('country_id', 'year', 'week').first()
        if weekly_status:
            country.date_of_join = weekly_status.date
            country.save()


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0005_auto_20200915_0723'),
    ]

    operations = [
        migrations.AddField(
            model_name='country',
            name='date_of_join',
            field=models.DateField(null=True),
        ),
        migrations.RunPython(fill_date_of_join, migrations.RunPython.noop),
    ]
