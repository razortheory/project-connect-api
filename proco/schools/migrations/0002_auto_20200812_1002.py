# Generated by Django 2.2.15 on 2020-08-12 10:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='school',
            name='admin_2_name',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='school',
            name='admin_3_name',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='school',
            name='admin_4_name',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='school',
            name='external_id',
            field=models.CharField(blank=True, db_index=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='school',
            name='address',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='school',
            name='altitude',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='school',
            name='education_level',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AlterField(
            model_name='school',
            name='environment',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AlterField(
            model_name='school',
            name='postal_code',
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AlterField(
            model_name='school',
            name='school_type',
            field=models.CharField(blank=True, max_length=64),
        ),
    ]
