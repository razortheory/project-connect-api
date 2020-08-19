from django.db import models
from django.utils.translation import ugettext as _

from model_utils import Choices
from model_utils.models import TimeStampedModel

from proco.locations.models import Country
from proco.schools.models import School
from proco.utils.utils import get_current_week, get_current_weekday, get_current_year


class ConnectivityStatistics(models.Model):
    connectivity_speed = models.FloatField(blank=True, null=True, default=None)
    connectivity_latency = models.PositiveSmallIntegerField(blank=True, null=True, default=None)

    class Meta:
        abstract = True


class CountryWeeklyStatus(models.Model):
    JOINED = 0
    SCHOOL_MAPPED = 1
    STATIC_MAPPED = 2
    REALTIME_MAPPED = 3
    INTEGRATION_STATUS_TYPES = Choices(
        (JOINED, _('Country Joined Project Connect')),
        (SCHOOL_MAPPED, _('School locations mapped')),
        (STATIC_MAPPED, _('Static connectivity mapped')),
        (REALTIME_MAPPED, _('Real time connectivity mapped')),
    )

    country = models.ForeignKey(Country, related_name='weekly_status', on_delete=models.CASCADE)
    year = models.PositiveSmallIntegerField(default=get_current_year)
    week = models.PositiveSmallIntegerField(default=get_current_week)
    schools_total = models.PositiveIntegerField(blank=True, null=True, default=None)
    schools_connected = models.PositiveIntegerField(blank=True, null=True, default=None)
    schools_connectivity_unknown = models.PositiveIntegerField(blank=True, null=True, default=None)
    schools_connectivity_no = models.PositiveIntegerField(blank=True, null=True, default=None)
    schools_connectivity_moderate = models.PositiveIntegerField(blank=True, null=True, default=None)
    schools_connectivity_good = models.PositiveIntegerField(blank=True, null=True, default=None)
    connectivity_speed = models.FloatField(blank=True, null=True, default=None)
    integration_status = models.PositiveSmallIntegerField(choices=INTEGRATION_STATUS_TYPES, default=JOINED)
    avg_distance_school = models.FloatField(blank=True, null=True, default=None)

    class Meta:
        verbose_name = _('Country Weekly Status')
        verbose_name_plural = _('Country Weekly Statuses')
        ordering = ('id',)

    def __str__(self):
        return f'{self.year} {self.country.name} Week {self.week} Speed - {self.connectivity_speed}'


class SchoolWeeklyStatus(models.Model):
    CONNECTIVITY_STATUS_TYPES = Choices(
        ('unknown', _('Unknown')),
        ('no', _('No')),
        ('2g', _('2G')),
        ('3g', _('3G')),
        ('4g', _('4G')),
        ('fiber', _('Fiber')),
        ('cable', _('Cable')),
        ('dsl', _('DSL')),
    )

    school = models.ForeignKey(School, related_name='weekly_status', on_delete=models.CASCADE)
    year = models.PositiveSmallIntegerField(default=get_current_year)
    week = models.PositiveSmallIntegerField(default=get_current_week)
    num_students = models.PositiveSmallIntegerField(blank=True, null=True, default=None)
    num_teachers = models.PositiveSmallIntegerField(blank=True, null=True, default=None)
    num_classroom = models.PositiveSmallIntegerField(blank=True, null=True, default=None)
    num_latrines = models.PositiveSmallIntegerField(blank=True, null=True, default=None)
    running_water = models.BooleanField(default=False)
    electricity_availability = models.BooleanField(default=False)
    computer_lab = models.BooleanField(default=False)
    num_computers = models.PositiveSmallIntegerField(blank=True, null=True, default=None)
    connectivity = models.BooleanField(default=False)
    connectivity_status = models.CharField(max_length=64, default='unknown')
    connectivity_speed = models.FloatField(blank=True, null=True, default=None)
    connectivity_latency = models.PositiveSmallIntegerField(blank=True, null=True, default=None)
    connectivity_availability = models.FloatField(blank=True, null=True, default=None)

    class Meta:
        verbose_name = _('School Weekly Status')
        verbose_name_plural = _('School Weekly Statuses')
        ordering = ('id',)

    def __str__(self):
        return f'{self.year} {self.school.name} Week {self.week} Speed - {self.connectivity_speed}'


class CountryDailyStatus(ConnectivityStatistics, models.Model):
    country = models.ForeignKey(Country, related_name='daily_status', on_delete=models.CASCADE)
    year = models.PositiveSmallIntegerField(default=get_current_year)
    week = models.PositiveSmallIntegerField(default=get_current_week)
    weekday = models.PositiveSmallIntegerField(default=get_current_weekday)

    class Meta:
        verbose_name = _('Country Daily Status')
        verbose_name_plural = _('Country Daily Statuses')
        ordering = ('id',)

    def __str__(self):
        return f'{self.year} {self.country.name} Week {self.week} Day {self.weekday} Speed - {self.connectivity_speed}'


class SchoolDailyStatus(ConnectivityStatistics, models.Model):
    school = models.ForeignKey(School, related_name='daily_status', on_delete=models.CASCADE)
    year = models.PositiveSmallIntegerField(default=get_current_year)
    week = models.PositiveSmallIntegerField(default=get_current_week)
    weekday = models.PositiveSmallIntegerField(default=get_current_weekday)

    class Meta:
        verbose_name = _('School Daily Status')
        verbose_name_plural = _('School Daily Statuses')
        ordering = ('id',)

    def __str__(self):
        return f'{self.year} {self.school.name} Week {self.week} Day {self.weekday} Speed - {self.connectivity_speed}'


class RealTimeConnectivity(ConnectivityStatistics, TimeStampedModel):
    school = models.ForeignKey(School, related_name='realtime_status', on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Real Time Connectivity')
        verbose_name_plural = _('Real Time Connectivities')
        ordering = ('id',)

    def __str__(self):
        return f'{self.created} {self.school.name} Speed - {self.connectivity_speed}'
