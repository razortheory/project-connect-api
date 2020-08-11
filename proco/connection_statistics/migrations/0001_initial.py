# Generated by Django 2.2.15 on 2020-08-11 14:33

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import proco.utils.utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('locations', '0001_initial'),
        ('schools', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SchoolWeeklyStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.PositiveSmallIntegerField(default=proco.utils.utils.get_current_year)),
                ('week', models.PositiveSmallIntegerField(default=proco.utils.utils.get_current_week)),
                ('num_students', models.PositiveSmallIntegerField(blank=True, default=None, null=True)),
                ('num_teachers', models.PositiveSmallIntegerField(blank=True, default=None, null=True)),
                ('num_classroom', models.PositiveSmallIntegerField(blank=True, default=None, null=True)),
                ('num_latrines', models.PositiveSmallIntegerField(blank=True, default=None, null=True)),
                ('running_water', models.BooleanField(default=False)),
                ('electricity_availability', models.BooleanField(default=False)),
                ('computer_lab', models.BooleanField(default=False)),
                ('num_computers', models.PositiveSmallIntegerField(blank=True, default=None, null=True)),
                ('connectivity_status', models.CharField(choices=[('unknown', 'Unknown'), ('no', 'No'), ('2g', '2G'), ('3g', '3G'), ('4g', '4G'), ('fiber', 'Fiber'), ('cable', 'Cable'), ('dsl', 'DSL')], default='unknown', max_length=64)),
                ('connectivity_speed', models.DecimalField(blank=True, decimal_places=2, default=None, max_digits=6, null=True)),
                ('connectivity_latency', models.PositiveSmallIntegerField(blank=True, default=None, null=True)),
                ('connectivity_availability', models.DecimalField(blank=True, decimal_places=2, default=None, max_digits=4, null=True)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='weekly_status', to='schools.School')),
            ],
            options={
                'verbose_name': 'School Weekly Status',
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='SchoolDailyStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('connectivity_speed', models.DecimalField(blank=True, decimal_places=2, default=None, max_digits=6, null=True)),
                ('connectivity_latency', models.PositiveSmallIntegerField(blank=True, default=None, null=True)),
                ('year', models.PositiveSmallIntegerField(default=proco.utils.utils.get_current_year)),
                ('week', models.PositiveSmallIntegerField(default=proco.utils.utils.get_current_week)),
                ('weekday', models.PositiveSmallIntegerField(default=proco.utils.utils.get_current_weekday)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='daily_status', to='schools.School')),
            ],
            options={
                'verbose_name': 'School Daily Status',
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='RealTimeConnectivity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('connectivity_speed', models.DecimalField(blank=True, decimal_places=2, default=None, max_digits=6, null=True)),
                ('connectivity_latency', models.PositiveSmallIntegerField(blank=True, default=None, null=True)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='realtime_status', to='schools.School')),
            ],
            options={
                'verbose_name': 'Country Weekly Status',
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='CountryWeeklyStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.PositiveSmallIntegerField(default=proco.utils.utils.get_current_year)),
                ('week', models.PositiveSmallIntegerField(default=proco.utils.utils.get_current_week)),
                ('schools_total', models.PositiveIntegerField(blank=True, default=None, null=True)),
                ('schools_connected', models.PositiveIntegerField(blank=True, default=None, null=True)),
                ('schools_connectivity_unknown', models.PositiveIntegerField(blank=True, default=None, null=True)),
                ('schools_connectivity_no', models.PositiveIntegerField(blank=True, default=None, null=True)),
                ('schools_connectivity_moderate', models.PositiveIntegerField(blank=True, default=None, null=True)),
                ('schools_connectivity_good', models.PositiveIntegerField(blank=True, default=None, null=True)),
                ('connectivity_speed', models.DecimalField(blank=True, decimal_places=2, default=None, max_digits=6, null=True)),
                ('integration_status', models.PositiveSmallIntegerField(choices=[(0, 'Country Joined Project Connect'), (1, 'School locations mapped'), (2, 'Static connectivity mapped'), (3, 'Real time connectivity mapped')], default=0)),
                ('avg_distance_school', models.FloatField(blank=True, default=None, null=True)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='weekly_status', to='locations.Country')),
            ],
            options={
                'verbose_name': 'Country Weekly Status',
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='CountryDailyStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('connectivity_speed', models.DecimalField(blank=True, decimal_places=2, default=None, max_digits=6, null=True)),
                ('connectivity_latency', models.PositiveSmallIntegerField(blank=True, default=None, null=True)),
                ('year', models.PositiveSmallIntegerField(default=proco.utils.utils.get_current_year)),
                ('week', models.PositiveSmallIntegerField(default=proco.utils.utils.get_current_week)),
                ('weekday', models.PositiveSmallIntegerField(default=proco.utils.utils.get_current_weekday)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='daily_status', to='locations.Country')),
            ],
            options={
                'verbose_name': 'Country Daily Status',
                'ordering': ('id',),
            },
        ),
    ]
