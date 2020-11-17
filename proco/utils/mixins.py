from rest_framework.response import Response

from proco.utils.cache import cache_manager


class CachedListMixin(object):
    LIST_CACHE_KEY_PREFIX = None

    def get_list_cache_key(self):
        return '{0}_{1}'.format(
            getattr(self.__class__, 'LIST_CACHE_KEY_PREFIX', self.__class__.__name__) or self.__class__.__name__,
            "_".join(map(lambda  x: "{0}_{1}".format(x[0], x[1]), sorted(self.request.query_params.items())))
        )

    def list(self, request, *args, **kwargs):
        cache_key = self.get_list_cache_key()

        def wrapper():
            response = super(CachedListMixin, self).list(request, *args, **kwargs)
            return response.data

        data = cache_manager.get(cache_key, calculate_func=wrapper)
        return Response(data=data)


class CachedRetrieveMixin(object):
    RETRIEVE_CACHE_KEY_PREFIX = None

    def get_retrieve_cache_key(self):
        return '{0}_{1}'.format(
            getattr(self.__class__, 'RETRIEVE_CACHE_KEY_PREFIX', self.__class__.__name__) or self.__class__.__name__,
            "_".join(map(lambda  x: "{0}_{1}".format(x[0], x[1]), sorted(self.kwargs.items())))
        )

    def retrieve(self, request, *args, **kwargs):
        cache_key = self.get_retrieve_cache_key()

        def wrapper():
            response = super(CachedRetrieveMixin, self).retrieve(request, *args, **kwargs)
            return response.data

        data = cache_manager.get(cache_key, calculate_func=wrapper)
        return Response(data=data)