from django.apps import AppConfig


class LocationsConfig(AppConfig):
    name = 'proco.locations'
    verbose_name = 'Locations'

    def ready(self):
        from proco.locations import signals  # NOQA

    GET_CACHE_KEY = {
        'countries-list': 'proco.locations.cache.get_cache_countries_key',
    }
    CACHE_COUNTRIES_VERSION_KEY = 'countries-etag-version'
