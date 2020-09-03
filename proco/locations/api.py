from django.db.models import Prefetch

from rest_framework import mixins, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

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
        OrderingFilter, SearchFilter,
    )
    ordering = ('name',)
    ordering_fields = ('name',)
    search_fields = ('name',)

    def get_serializer_class(self):
        if self.action == 'list':
            serializer_class = ListCountrySerializer
        else:
            serializer_class = DetailCountrySerializer
        return serializer_class
