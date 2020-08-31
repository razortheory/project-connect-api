import re

from django.apps import apps
from django.core.cache import cache
from django.utils.text import slugify

from rest_framework.request import Request

CONF = apps.get_app_config('schools')


def get_cache_schools_version(url: str):
    country_id = re.search(r'countries(\d)schools$', url)[1]
    cache_version_key = cache.get(CONF.CACHE_SCHOOLS_VERSION_KEY.format(country_id=country_id)) or 0
    return cache_version_key


def invalidate_cache(country_id: int):
    """
    Invalidate the schools etag in the cache on every change.
    """
    key = CONF.CACHE_SCHOOLS_VERSION_KEY.format(country_id=str(country_id))
    try:
        cache.incr(key)
    except ValueError:
        cache.set(key, 1)


def get_cache_schools_key(request: Request):
    url = str(request._request.get_raw_uri())
    return f'schools-etag-{get_cache_schools_version(slugify(url))}-{slugify(url)}'
