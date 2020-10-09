import math

from django.contrib.gis.db.models import MultiPolygonField
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon, Polygon
from django.db import models
from django.utils.translation import ugettext as _

import numpy as np
from model_utils.models import TimeStampedModel
from mptt.models import MPTTModel, TreeForeignKey
from sklearn.neighbors import DistanceMetric

from proco.locations.utils import get_random_name_image


class GeometryMixin(models.Model):
    geometry = MultiPolygonField(verbose_name=_('Country border geometry'), null=True, blank=True)
    geometry_simplified = MultiPolygonField(verbose_name=_('Simplified Geometry'), null=True, blank=True)

    class Meta:
        abstract = True

    @classmethod
    def to_multipolygon(cls, geos_geom: [MultiPolygon, Polygon]) -> MultiPolygon:
        return MultiPolygon(geos_geom) if isinstance(geos_geom, Polygon) else geos_geom

    @classmethod
    def optimize_geometry(cls, geometry: [GEOSGeometry]) -> [MultiPolygon]:
        if geometry is None:
            return geometry

        # magic numbers
        tolerance = 0.03
        tolerance_divider = 4
        max_attempts = 5

        for _i in range(max_attempts):
            geometry_simplified = geometry.simplify(tolerance=tolerance)
            if not geometry_simplified.empty:
                return cls.to_multipolygon(geometry_simplified)

            tolerance = tolerance / tolerance_divider

        return geometry

    def save(self, *args, **kwargs):
        self.geometry_simplified = self.optimize_geometry(self.geometry)

        super().save(*args, **kwargs)


class Country(GeometryMixin, TimeStampedModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=32)

    flag = models.ImageField(verbose_name=_('Country flag'), upload_to=get_random_name_image)
    map_preview = models.ImageField(upload_to=get_random_name_image, null=True, blank=True, default=None)

    description = models.TextField(max_length=1000, blank=True, default='')
    data_source = models.TextField(max_length=500, blank=True, default='')

    date_of_join = models.DateField(null=True)

    class Meta:
        ordering = ('name',)
        verbose_name = _('Country')
        verbose_name_plural = _('Countries')

    def __str__(self):
        return f'{self.name}'

    def _calculate_avg_distance_school_for_batch(self, points):
        # mean Earth radius
        earth_radius = 6371.0088
        dist = DistanceMetric.get_metric('haversine')
        distances = dist.pairwise(np.radians(points))
        indexes = np.tril_indices(n=distances.shape[0], k=-1, m=distances.shape[1])
        return np.mean(distances[indexes]) * earth_radius

    def calculate_avg_distance_school(self):
        schools_count = self.schools.count()

        if schools_count < 2:
            return None
        elif schools_count <= 10000:
            return self._calculate_avg_distance_school_for_batch(
                self.schools.annotate(
                    lon=models.Func(models.F('geopoint'), function='ST_X', output_field=models.FloatField()),
                    lat=models.Func(models.F('geopoint'), function='ST_Y', output_field=models.FloatField()),
                ).values_list('lat', 'lon'),
            )
        else:
            cluster_number = math.ceil(schools_count / 5000.)

            avg_distances = []
            weights = []
            for cluster in range(0, cluster_number):
                schools = self.schools.raw(
                    """
                        SELECT a.id, a.cluster, a.lat, a.lon FROM (
                            SELECT *, ST_ClusterKMeans(geopoint, {0}) over () AS cluster,
                                   ST_X(geopoint) AS lon, ST_Y(geopoint) AS lat
                            FROM schools_school
                        ) as a WHERE cluster = {1} AND country_id = {2} ORDER BY cluster;
                    """.format(cluster_number, cluster, self.id),
                )
                schools_points = list(map(lambda x: (x.lat, x.lon), schools))

                if len(schools_points) > 1:
                    avg_distances.append(self._calculate_avg_distance_school_for_batch(schools_points))
                    weights.append(len(schools_points))
            return np.average(avg_distances, weights=weights)


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
