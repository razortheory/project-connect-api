from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import ugettext as _

from isoweek import Week
from model_utils import Choices
from model_utils.models import TimeStampedModel

from proco.locations.models import Country
from proco.schools.models import School
from proco.utils.dates import get_current_week, get_current_year


class ConnectivityStatistics(models.Model):
    connectivity_speed = models.PositiveIntegerField(help_text=_('bps'), blank=True, null=True, default=None)
    connectivity_latency = models.PositiveSmallIntegerField(help_text=_('ms'), blank=True, null=True, default=None)

    class Meta:
        abstract = True


class CountryWeeklyStatus(ConnectivityStatistics, TimeStampedModel, models.Model):
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
    date = models.DateField()
    schools_total = models.PositiveIntegerField(blank=True, default=0)
    schools_connected = models.PositiveIntegerField(blank=True, default=0)
    schools_connectivity_unknown = models.PositiveIntegerField(blank=True, default=0)
    schools_connectivity_no = models.PositiveIntegerField(blank=True, default=0)
    schools_connectivity_moderate = models.PositiveIntegerField(blank=True, default=0)
    schools_connectivity_good = models.PositiveIntegerField(blank=True, default=0)
    integration_status = models.PositiveSmallIntegerField(choices=INTEGRATION_STATUS_TYPES, default=JOINED)
    avg_distance_school = models.FloatField(blank=True, default=None, null=True)
    schools_with_data_percentage = models.DecimalField(
        decimal_places=5, max_digits=6, default=0, validators=[MaxValueValidator(1), MinValueValidator(0)],
    )

    class Meta:
        verbose_name = _('Country Summary')
        verbose_name_plural = _('Country Summary')
        ordering = ('id',)
        unique_together = ('year', 'week', 'country')

    def __str__(self):
        return f'{self.year} {self.country.name} Week {self.week} Speed - {self.connectivity_speed}'

    def save(self, **kwargs):
        self.date = Week(self.year, self.week).monday()
        super().save(**kwargs)


class SchoolWeeklyStatus(ConnectivityStatistics, TimeStampedModel, models.Model):
    CONNECTIVITY_TYPES = Choices(
        ('unknown', _('Unknown')),
        ('no', _('No')),
        ('2g', _('2G')),
        ('3g', _('3G')),
        ('4g', _('4G')),
        ('fiber', _('Fiber')),
        ('cable', _('Cable')),
        ('dsl', _('DSL')),
    )
    CONNECTIVITY_STATUSES = Choices(
        ('no', _('No connectivity')),
        ('unknown', _('Data unavailable')),
        ('moderate', _('Moderate')),
        ('good', _('Good')),
    )
    COVERAGE_TYPES = Choices(
        ('unknown', _('Unknown')),
        ('no', _('No')),
        ('2g', _('2G')),
        ('3g', _('3G')),
        ('4g', _('4G')),
    )

    school = models.ForeignKey(School, related_name='weekly_status', on_delete=models.CASCADE)
    year = models.PositiveSmallIntegerField(default=get_current_year)
    week = models.PositiveSmallIntegerField(default=get_current_week)
    date = models.DateField()
    num_students = models.PositiveSmallIntegerField(blank=True, default=0)
    num_teachers = models.PositiveSmallIntegerField(blank=True, default=0)
    num_classroom = models.PositiveSmallIntegerField(blank=True, default=0)
    num_latrines = models.PositiveSmallIntegerField(blank=True, default=0)
    running_water = models.BooleanField(default=False)
    electricity_availability = models.BooleanField(default=False)
    computer_lab = models.BooleanField(default=False)
    num_computers = models.PositiveSmallIntegerField(blank=True, default=0)
    connectivity = models.NullBooleanField(default=None)
    connectivity_status = models.CharField(max_length=8, default=CONNECTIVITY_STATUSES.unknown,
                                           choices=CONNECTIVITY_STATUSES, db_index=True)
    connectivity_type = models.CharField(_('Type of internet connection'), max_length=64, default='unknown')
    coverage_availability = models.NullBooleanField(default=None)
    coverage_type = models.CharField(max_length=8, default=COVERAGE_TYPES.unknown,
                                     choices=COVERAGE_TYPES)

    class Meta:
        verbose_name = _('School Summary')
        verbose_name_plural = _('School Summary')
        ordering = ('id',)
        unique_together = ('year', 'week', 'school')

    def __str__(self):
        return f'{self.year} {self.school.name} Week {self.week} Speed - {self.connectivity_speed}'

    def save(self, **kwargs):
        self.date = self.get_date()
        self.connectivity_status = self.get_connectivity_status()
        if self.coverage_availability is None:
            self.coverage_type, self.coverage_availability = self.get_coverage_type_and_status()
        super().save(**kwargs)

    def get_date(self):
        return Week(self.year, self.week).monday()

    def get_connectivity_status(self):
        if self.connectivity is False:
            return self.CONNECTIVITY_STATUSES.no

        if self.connectivity is None or not self.connectivity_speed:
            return self.CONNECTIVITY_STATUSES.unknown

        if self.connectivity_speed > 5 * (10 ** 6):
            return self.CONNECTIVITY_STATUSES.good
        else:
            return self.CONNECTIVITY_STATUSES.moderate

    def get_coverage_type_and_status(self):
        coverage_type = self.COVERAGE_TYPES.unknown
        coverage_availability = None

        if self.connectivity_type and self.connectivity_type.lower() != self.CONNECTIVITY_TYPES.unknown:
            coverage_availability = True
            for coverage in ['2g', '3g', '4g']:
                if coverage in self.connectivity_type.lower():
                    coverage_type = coverage

        if self.connectivity_type and self.connectivity_type.lower() in ['no covered', 'no', 'no service']:
            coverage_type = SchoolWeeklyStatus.COVERAGE_TYPES.no
            coverage_availability = False

        return coverage_type, coverage_availability


class CountryDailyStatus(ConnectivityStatistics, TimeStampedModel, models.Model):
    country = models.ForeignKey(Country, related_name='daily_status', on_delete=models.CASCADE)
    date = models.DateField()

    class Meta:
        verbose_name = _('Country Daily Connectivity Summary')
        verbose_name_plural = _('Country Daily Connectivity Summary')
        ordering = ('id',)
        unique_together = ('date', 'country')

    def __str__(self):
        year, week, weekday = self.date.isocalendar()
        return f'{year} {self.country.name} Week {week} Day {weekday} Speed - {self.connectivity_speed}'


class SchoolDailyStatus(ConnectivityStatistics, TimeStampedModel, models.Model):
    school = models.ForeignKey(School, related_name='daily_status', on_delete=models.CASCADE)
    date = models.DateField()

    class Meta:
        verbose_name = _('School Daily Connectivity Summary')
        verbose_name_plural = _('School Daily Connectivity Summary')
        ordering = ('id',)
        unique_together = ('date', 'school')

    def __str__(self):
        year, week, weekday = self.date.isocalendar()
        return f'{year} {self.school.name} Week {week} Day {weekday} Speed - {self.connectivity_speed}'


class RealTimeConnectivity(ConnectivityStatistics, TimeStampedModel, models.Model):
    school = models.ForeignKey(School, related_name='realtime_status', on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Real Time Connectivity Data')
        verbose_name_plural = _('Real Time Connectivity Data')
        ordering = ('id',)

    def __str__(self):
        return f'{self.created} {self.school.name} Speed - {self.connectivity_speed}'
