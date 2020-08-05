from django.contrib.gis.db.models import PointField
from django.db import models
from django.utils.translation import ugettext as _

from model_utils import Choices
from model_utils.models import TimeStampedModel
from phonenumber_field.modelfields import PhoneNumberField
from timezone_field import TimeZoneField

from proco.locations.models import Country, Location


class School(TimeStampedModel):
    EDUCATION_LEVEL_TYPES = Choices(
        'preschool', _('Early childhood education'),
        'primary', _('Primary education'),
        'secondary', _('Secondary education'),
    )
    ENVIRONMENT_TYPES = Choices(
        'urban', _('Urban'),
        'semi_rural', _('Semi-rural'),
        'rural', _('Rural'),
    )
    SCHOOL_TYPES = Choices(
        'private', _('Private'),
        'government', _('Government'),
        'religious', _('Religious'),
    )
    name = models.CharField(max_length=255)
    country = models.ForeignKey(Country, related_name='schools', on_delete=models.CASCADE)
    location = models.ForeignKey(Location, related_name='schools', on_delete=models.CASCADE)
    timezone = TimeZoneField()
    geopoint = PointField(verbose_name=_('Point'), null=True, blank=True)
    gps_confidence = models.DecimalField(max_digits=5, decimal_places=5)  # max_digits, decimal_places?
    altitude = models.PositiveIntegerField()
    address = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=128)
    phone_number = PhoneNumberField()
    contact_person = models.CharField(max_length=255)
    email = models.EmailField(max_length=128)
    education_level = models.CharField(max_length=64, choices=EDUCATION_LEVEL_TYPES,
                                       default=EDUCATION_LEVEL_TYPES.preschool)
    environment = models.CharField(max_length=64, choices=ENVIRONMENT_TYPES, default=ENVIRONMENT_TYPES.urban)
    school_type = models.CharField(max_length=64, choices=SCHOOL_TYPES, default=SCHOOL_TYPES.private)

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return f'{self.country} - {self.name}'
