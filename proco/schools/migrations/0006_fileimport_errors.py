# Generated by Django 2.2.15 on 2020-08-13 10:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0005_auto_20200813_0903'),
    ]

    operations = [
        migrations.AddField(
            model_name='fileimport',
            name='errors',
            field=models.TextField(blank=True),
        ),
    ]
