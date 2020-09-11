# from django.contrib.gis.db.models.aggregates import Union
# from django.contrib.gis.geos import MultiPolygon, Polygon
from django.db.models.signals import post_save
from django.dispatch import receiver

from proco.connection_statistics.models import CountryWeeklyStatus
from proco.locations.models import Country

#
#
# def to_multipolygon(geos_geom):
#     return MultiPolygon(geos_geom) if isinstance(geos_geom, Polygon) else geos_geom
#
#
# @receiver([post_save, post_delete], sender=Location)
# def recount_country_geometry(instance, created=False, **kwargs):
#     qs = Location.objects.filter(parent__isnull=True, country=instance.country)
#     union_geometry = qs.aggregate(geometry=Union('geometry'))['geometry']
#     instance.country.geometry = to_multipolygon(union_geometry)
#     instance.country.save()


@receiver(post_save, sender=Country)
def create_country_weekly_status(instance, created=False, **kwargs):
    if created:
        CountryWeeklyStatus.objects.create(country=instance)
