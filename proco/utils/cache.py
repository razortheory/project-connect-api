import uuid
from functools import wraps

from django.core.cache import cache
from django.utils.cache import patch_cache_control
from rest_framework import status
from rest_framework.response import Response

from django.apps import apps
from django.urls import get_callable


def etag_cached(app: str, cache_name: str):
    """
    Returns list of instances only if there's a new ETag, and it does not
    match the one sent along with the request.
    Otherwise it returns 304 NOT MODIFIED.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            conf = apps.get_app_config(app)
            func_ = get_callable(conf.GET_CACHE_KEY[cache_name])
            key = func_(self.request)
            cache_etag = cache.get(key)
            request_etag = self.request.META.get("HTTP_IF_NONE_MATCH", None)
            local_etag = cache_etag if cache_etag else '"{}"'.format(uuid.uuid4().hex)

            if cache_etag and request_etag and cache_etag == request_etag:
                response = Response(status=status.HTTP_304_NOT_MODIFIED)
            else:
                response = func(self, *args, **kwargs)
                response["ETag"] = local_etag

            if not cache_etag:
                cache.set(key, local_etag)

            patch_cache_control(response, private=True, must_revalidate=True)

            return response

        return wrapper

    return decorator
