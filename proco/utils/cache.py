from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from proco.taskapp import app


class SoftCacheManager(object):
    CACHE_PREFIX = 'SOFT_CACHE'

    def get(self, key, calculate_func=None, soft_timeout=settings.CACHES['default']['TIMEOUT']):
        value = cache.get('{0}_{1}'.format(self.CACHE_PREFIX, key), None)

        if value:
            if (
                    (value['expired_at'] and value['expired_at'] < timezone.now().timestamp())
                    or value.get('invalidated', False)
            ):

                def update_value():
                    value = calculate_func()
                    self.set(key, value, soft_timeout)

                app.task(update_value).delay()
            return value['value']
        elif calculate_func:
            value = calculate_func()
            self.set(key, value, soft_timeout)
            return value

    def _invalidate(self, key):
        value = cache.get(key, None)
        if value:
            value['invalidated'] = True
            cache.set(key, value, None)

    def invalidate_many(self, keys):
        for key in keys:
            self.invalidate(key)

    def invalidate(self, key='*'):
        if isinstance(key, str):
            keys = cache.keys('{0}_{1}'.format(self.CACHE_PREFIX, key))
            for key in keys:
                self._invalidate(key)
        elif isinstance(key, (list, tuple)):
            self.invalidate_many(key)

    def set(self, key, value, soft_timeout=None):
        cache.set('{0}_{1}'.format(self.CACHE_PREFIX, key), {
            'value': value,
            'expired_at': timezone.now().timestamp() + soft_timeout if soft_timeout else None,
        }, None)


cache_manager = SoftCacheManager()
