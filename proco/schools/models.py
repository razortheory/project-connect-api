from django.conf import settings
from django.contrib.gis.db.models import PointField
from django.db import models
from django.db.models import OuterRef, Subquery
from django.utils.translation import ugettext as _

from model_utils import Choices
from model_utils.models import TimeStampedModel
from timezone_field import TimeZoneField

from proco.locations.models import Country, Location
from proco.schools.utils import get_imported_file_path


class SchoolManager(models.Manager):
    def annotate_status_connectivity(self):
        from proco.connection_statistics.models import SchoolWeeklyStatus
        return self.get_queryset().annotate(
            connectivity=Subquery(
                SchoolWeeklyStatus.objects.filter(
                    school=OuterRef('id'),
                ).order_by('-id')[:1].values('connectivity'),
            ),
        )


class School(TimeStampedModel):
    external_id = models.CharField(max_length=50, blank=True, db_index=True)
    name = models.CharField(max_length=255)

    country = models.ForeignKey(Country, related_name='schools', on_delete=models.CASCADE)
    location = models.ForeignKey(Location, null=True, blank=True, related_name='schools', on_delete=models.CASCADE)
    admin_1_name = models.CharField(max_length=100, blank=True)
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

    objects = SchoolManager()

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return f'{self.country} - {self.name}'


class FileImport(TimeStampedModel):
    STATUSES = Choices(
        ('pending', _('Pending')),
        ('started', _('Started')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
    )
    PROCESS_STATUSES = [STATUSES.pending, STATUSES.started, ]

    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_file = models.FileField(upload_to=get_imported_file_path)
    status = models.CharField(max_length=10, choices=STATUSES, default=STATUSES.pending)
    errors = models.TextField(blank=True)

    def __str__(self):
        return self.uploaded_file.name

    class Meta:
        ordering = ('id',)
