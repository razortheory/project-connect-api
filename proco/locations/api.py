from django.conf import settings
from django.db.models import Prefetch
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework import mixins, viewsets
from rest_framework.filters import OrderingFilter

from proco.connection_statistics.models import CountryWeeklyStatus
from proco.locations.models import Country
from proco.locations.serializers import CountrySerializer, DetailCountrySerializer, ListCountrySerializer


class CountryViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    pagination_class = None
    queryset = Country.objects.all().prefetch_related(
        Prefetch(
            'weekly_status',
            CountryWeeklyStatus.objects.order_by('country_id', '-year', '-week').distinct('country_id'),
            to_attr='latest_status',
        ),
    )
    serializer_class = CountrySerializer
    filter_backends = (
        OrderingFilter,
    )
    ordering = ('name',)
    ordering_fields = ('name',)

    def get_serializer_class(self):
        if self.action == 'list':
            serializer_class = ListCountrySerializer
        else:
            serializer_class = DetailCountrySerializer
        return serializer_class

    @method_decorator(cache_page(timeout=settings.CACHES['default']['TIMEOUT']))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
