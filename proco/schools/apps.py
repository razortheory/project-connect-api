from django.apps import AppConfig


class SchoolsConfig(AppConfig):
    name = 'proco.schools'
    verbose_name = 'Schools'

    def ready(self):
        from proco.schools import signals  # NOQA

    GET_CACHE_KEY = {
        'schools-list': 'proco.schools.cache.get_cache_schools_key',
    }
    CACHE_SCHOOLS_VERSION_KEY = 'schools-etag-country-{country_id}'
