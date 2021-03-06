# Generated by Django 2.2.15 on 2021-03-03 08:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custom_auth', '0006_applicationuser_countries_available'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applicationuser',
            name='countries_available',
            field=models.ManyToManyField(blank=True, help_text='Countries to which the user has access and the ability to manage them.', related_name='countries_available', to='locations.Country', verbose_name='Сountries Available'),
        ),
    ]
