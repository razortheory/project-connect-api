from django.db.models import BooleanField, F, Func
from django.shortcuts import get_object_or_404

from rest_framework import mixins, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView

from proco.locations.models import Country
from proco.locations.serializers import (
    BoundaryListCountrySerializer,
    CountrySerializer,
    DetailCountrySerializer,
    ListCountrySerializer,
)
from proco.utils.filters import NullsAlwaysLastOrderingFilter
from proco.utils.mixins import CachedListMixin, CachedRetrieveMixin


class CountryViewSet(
    CachedListMixin,
    CachedRetrieveMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    LIST_CACHE_KEY_PREFIX = 'COUNTRIES_LIST'
    RETRIEVE_CACHE_KEY_PREFIX = 'COUNTRY_INFO'

    pagination_class = None
    queryset = Country.objects.all().annotate(
        geometry_empty=Func(F('geometry'), function='ST_IsEmpty', output_field=BooleanField()),
    ).select_related('last_weekly_status').filter(geometry_empty=False)
    serializer_class = CountrySerializer
    filter_backends = (
        NullsAlwaysLastOrderingFilter, SearchFilter,
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

    def get_object(self):
        country_pointer = self.kwargs.get('pk')
        if not country_pointer.isdigit():
            return get_object_or_404(self.queryset, code__iexact=country_pointer)
        return super().get_object()

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == 'list':
            qs = qs.defer('geometry', 'geometry_simplified')
        return qs


class CountryBoundaryListAPIView(CachedListMixin, ListAPIView):
    LIST_CACHE_KEY_PREFIX = 'COUNTRY_BOUNDARY'

    queryset = Country.objects.all().annotate(
        geometry_empty=Func(F('geometry'), function='ST_IsEmpty', output_field=BooleanField()),
    ).filter(geometry_empty=False).only('id', 'geometry_simplified')
    serializer_class = BoundaryListCountrySerializer
    pagination_class = None
