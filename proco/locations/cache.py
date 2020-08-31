from django.apps import apps
from django.core.cache import cache
from django.utils.text import slugify

from rest_framework.request import Request

CONF = apps.get_app_config('locations')


def get_cache_countries_version():
    return cache.get(CONF.CACHE_COUNTRIES_VERSION_KEY) or 0


def invalidate_cache():
    """
    Invalidate the locations etag in the cache on every change.
    """
    try:
        cache.incr(CONF.CACHE_COUNTRIES_VERSION_KEY)
    except ValueError:
        cache.set(CONF.CACHE_COUNTRIES_VERSION_KEY, 1)


def get_cache_countries_key(request: Request):
    url = str(request._request.get_raw_uri())
    return f'countries-etag-{get_cache_countries_version()}-{slugify(url)}'
