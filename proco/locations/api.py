from django.db.models import Prefetch

from rest_framework import mixins, viewsets
from rest_framework.filters import SearchFilter

from proco.connection_statistics.models import CountryWeeklyStatus
from proco.locations.models import Country
from proco.locations.serializers import CountrySerializer, DetailCountrySerializer, ListCountrySerializer
from proco.utils.filters import NullsAlwaysLastOrderingFilter


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
    ).annotate_integration_status().annotate_date_of_join().annotate_schools_with_data_percentage()
    serializer_class = CountrySerializer
    filter_backends = (
        NullsAlwaysLastOrderingFilter, SearchFilter,
    )
    ordering = ('name',)
    ordering_fields = ('name', 'schools_with_data_percentage', 'integration_status', 'date_of_join',)
    search_fields = ('name',)

    def get_serializer_class(self):
        if self.action == 'list':
            serializer_class = ListCountrySerializer
        else:
            serializer_class = DetailCountrySerializer
        return serializer_class
