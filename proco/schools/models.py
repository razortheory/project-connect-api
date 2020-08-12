from django.contrib.gis.db.models import PointField
from django.db import models
from django.utils.translation import ugettext as _

from model_utils.models import TimeStampedModel
from timezone_field import TimeZoneField

from proco.locations.models import Country, Location


class School(TimeStampedModel):
    external_id = models.CharField(max_length=50, blank=True, db_index=True)
    name = models.CharField(max_length=255)

    country = models.ForeignKey(Country, related_name='schools', on_delete=models.CASCADE)
    location = models.ForeignKey(Location, null=True, blank=True, related_name='schools', on_delete=models.CASCADE)
    admin_2_name = models.CharField(max_length=100, blank=True)
    admin_3_name = models.CharField(max_length=100, blank=True)
    admin_4_name = models.CharField(max_length=100, blank=True)
    geopoint = PointField(verbose_name=_('Point'), null=True, blank=True)

    timezone = TimeZoneField(blank=True, null=True)
    gps_confidence = models.FloatField(null=True, blank=True)
    altitude = models.PositiveIntegerField(blank=True, null=True)
    address = models.CharField(blank=True, max_length=255)
    postal_code = models.CharField(blank=True, max_length=128)
    email = models.EmailField(max_length=128, null=True, blank=True, default=None)
    education_level = models.CharField(blank=True, max_length=64)
    environment = models.CharField(blank=True, max_length=64)
    school_type = models.CharField(blank=True, max_length=64)

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return f'{self.country} - {self.name}'
