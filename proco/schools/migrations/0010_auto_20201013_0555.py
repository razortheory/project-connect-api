# Generated by Django 2.2.16 on 2020-10-13 05:55

from django.db import migrations, models

def update_environment_field_choices(apps, schema_editor):
    School = apps.get_model("schools", "School")
    School.objects.filter(country__code="BR").update(
        environment=models.functions.Lower(models.F('environment'))
    )
    School.objects.filter(country__code="BR", environment="urbana").update(
        environment="urban"
    )


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0009_auto_20200923_0603'),
    ]

    operations = [
        migrations.RunPython(update_environment_field_choices, migrations.RunPython.noop),
    ]