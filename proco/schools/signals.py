from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from proco.schools.models import School
from proco.schools.cache import invalidate_cache


@receiver(post_delete, sender=School)
@receiver(post_save, sender=School)
def invalidate_schools_etag(sender, instance, **kwargs):
    """
    Invalidate the schools etag in the cache on every change.
    """
    invalidate_cache(instance.country.id)
