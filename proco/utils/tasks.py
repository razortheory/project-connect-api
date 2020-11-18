from urllib.parse import parse_qs, urlparse

from django.contrib.sites.models import Site
from django.urls import reverse

import requests

from proco.taskapp import app


@app.task
def update_cached_value(url):
    requests.get(url, params={'cache': False})


@app.task
def update_all_cached_values():
    from proco.locations.models import Country

    site = Site.objects.get_current()

    url = urlparse("http://" + site.domain)

    url = url._replace(path=reverse('connection_statistics:global-stat'))
    update_cached_value(url.geturl())

    url = url._replace(path=reverse('locations:countries-boundary'))
    update_cached_value(url.geturl())

    url = url._replace(path=reverse('locations:countries-list'))
    update_cached_value(url.geturl())

    url = url._replace(path=reverse('schools:random-schools'))
    update_cached_value(url.geturl())

    for country in Country.objects.all():
        url = url._replace(path=reverse('locations:countries-detail', kwargs={'pk': country.pk}))
        update_cached_value(url.geturl())

        url = url._replace(path=reverse('schools:schools-list', kwargs={'country_pk': country.pk}))
        update_cached_value(url.geturl())
