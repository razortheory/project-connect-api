from math import ceil

from django.conf import settings
from django.urls import reverse

from rest_framework.test import APIClient

from celery import chain

from proco.taskapp import app


@app.task(soft_time_limit=10 * 60, time_limit=11 * 60)
def update_cached_value(*args, url: str = '', params: dict = None, **kwargs):
    client = APIClient()
    data = {'cache': False}
    if params:
        data.update(params)
    client.get(url, data, format='json')


@app.task(soft_time_limit=5 * 60, time_limit=5 * 60)
def update_all_cached_values():
    from proco.locations.models import Country

    update_cached_value.delay(url=reverse('connection_statistics:global-stat'))
    update_cached_value.delay(url=reverse('locations:countries-boundary'))
    update_cached_value.delay(url=reverse('locations:countries-list'))
    update_cached_value.delay(url=reverse('schools:random-schools'))

    for country in Country.objects.all():
        schools_page_count = ceil(country.schools.count() / settings.SCHOOLS_LIST_PAGE_SIZE)
        chain([
            update_cached_value.s(url=reverse('locations:countries-detail', kwargs={'pk': country.code.lower()})),
            update_cached_value.s(url=reverse('schools:schools-v2-meta', kwargs={'pk': country.code.lower()})),
        ] + [
            update_cached_value.s(
                url=reverse('schools:schools-v2-list', kwargs={'country_code': country.code.lower()}),
                params={'page': page},
            )
            for page in range(1, schools_page_count + 1)
        ] + [
            update_cached_value.s(url=reverse('schools:schools-list', kwargs={'country_code': country.code.lower()})),
        ]).delay()


@app.task
def update_country_related_cache(country_code):
    from proco.locations.models import Country

    update_cached_value.delay(url=reverse('connection_statistics:global-stat'))
    update_cached_value.delay(url=reverse('locations:countries-list'))
    update_cached_value.delay(url=reverse('schools:random-schools'))
    update_cached_value.delay(url=reverse('locations:countries-detail', kwargs={'pk': country_code.lower()}))
    update_cached_value.delay(url=reverse('schools:schools-v2-meta', kwargs={'country_code': country_code.lower()}))

    country = Country.objects.get(code=country_code)
    for page in range(1, ceil(country.schools.count() / settings.SCHOOLS_LIST_PAGE_SIZE) + 1):
        update_cached_value.delay(
            url=reverse('schools:schools-v2-list', kwargs={'country_code': country_code.lower()}),
            params={'page': page},
        )

    update_cached_value.delay(url=reverse('schools:schools-list', kwargs={'country_code': country_code.lower()}))
