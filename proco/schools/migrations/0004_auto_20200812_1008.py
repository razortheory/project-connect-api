# Generated by Django 2.2.15 on 2020-08-12 10:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0003_auto_20200812_1006'),
    ]

    operations = [
        migrations.AlterField(
            model_name='school',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='schools', to='locations.Location'),
        ),
    ]
