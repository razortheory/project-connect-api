from rest_framework import mixins, viewsets
from rest_framework.filters import OrderingFilter

from proco.locations.models import Country
from proco.locations.serializers import CountrySerializer, DetailCountrySerializer, ListCountrySerializer


class CountryViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Country.objects.all().prefetch_related('weekly_status')
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
