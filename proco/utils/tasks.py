from django.urls import reverse

from rest_framework.test import APIClient

from proco.taskapp import app


@app.task
def update_cached_value(url):
    client = APIClient()
    client.get(url, {'cache': False}, format='json')


@app.task
def update_all_cached_values():
    from proco.locations.models import Country

    update_cached_value(reverse('connection_statistics:global-stat'))
    update_cached_value(reverse('locations:countries-boundary'))
    update_cached_value(reverse('locations:countries-list'))
    update_cached_value(reverse('schools:random-schools'))

    for country in Country.objects.all():
        update_cached_value(reverse('locations:countries-detail', kwargs={'pk': country.pk}))
        update_cached_value(reverse('schools:schools-list', kwargs={'country_pk': country.pk}))
