from django.contrib.gis.db.models import MultiPolygonField
from django.db import models
from django.db.models.functions import Cast
from django.utils.translation import ugettext as _

from model_utils.models import TimeStampedModel
from mptt.models import MPTTModel, TreeForeignKey

from proco.locations.utils import get_random_name_image


class GeometryMixin(models.Model):
    geometry = MultiPolygonField(verbose_name=_('Country border geometry'), null=True, blank=True)
    geometry_simplified = MultiPolygonField(verbose_name=_('Simplified Geometry'), null=True, blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.geometry:
            self.geometry_simplified = self.geometry.simplify(tolerance=0.03)

        super().save(*args, **kwargs)


class CountryQuerySet(models.QuerySet):
    def annotate_integration_status(self):
        from proco.connection_statistics.models import CountryWeeklyStatus

        return self.annotate(
            integration_status=models.Subquery(
                CountryWeeklyStatus.objects.filter(
                    country_id=models.OuterRef('id')
                ).order_by('-created').values('integration_status')[:1]
            )
        )

    def annotate_date_of_join(self):
        from proco.connection_statistics.models import CountryWeeklyStatus

        return self.annotate(
            date_of_join=models.Subquery(
                CountryWeeklyStatus.objects.filter(
                    country_id=models.OuterRef('id'),
                    integration_status=CountryWeeklyStatus.JOINED
                ).order_by('created').values('created')[:1]
            )
        )

    def annotate_connected_schools_percentage(self):
        from proco.connection_statistics.models import CountryWeeklyStatus

        return self.annotate(
            connected_schools_percentage=Cast(models.Subquery(
                CountryWeeklyStatus.objects.filter(
                    country_id=models.OuterRef('id'),
                    integration_status=CountryWeeklyStatus.JOINED
                ).order_by('-created').annotate(
                    percentage=models.ExpressionWrapper(
                        100.0 * models.F('schools_connected') / models.F('schools_total'),
                        output_field=models.DecimalField(decimal_places=2, max_digits=6)
                    ),
                ).values('percentage')[:1]
            ), models.DecimalField(decimal_places=2, max_digits=6))
        )


class Country(GeometryMixin, TimeStampedModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=32)

    flag = models.ImageField(verbose_name=_('Country flag'), upload_to=get_random_name_image)
    map_preview = models.ImageField(upload_to=get_random_name_image, null=True, blank=True, default=None)

    description = models.TextField(max_length=1000, null=True, blank=True)
    data_source = models.TextField(max_length=500, null=True, blank=True)

    objects = CountryQuerySet.as_manager()

    class Meta:
        ordering = ('name',)
        verbose_name = _('Country')
        verbose_name_plural = _('Countries')

    def __str__(self):
        return f'{self.name}'


class Location(GeometryMixin, TimeStampedModel, MPTTModel):
    name = models.CharField(max_length=255)
    country = models.ForeignKey(Country, related_name='country_location', on_delete=models.CASCADE)
    parent = TreeForeignKey(
        'self',
        related_name='children',
        null=True,
        blank=True,
        db_index=True,
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return f'{self.name} - {self.country}'
