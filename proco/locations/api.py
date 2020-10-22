from django.conf import settings
from django.db.models import BooleanField, F, Func
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

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


class CountryViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
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

    @method_decorator(cache_page(timeout=settings.CACHES['default']['TIMEOUT']))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @method_decorator(cache_page(timeout=settings.CACHES['default']['TIMEOUT']))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CountryBoundaryListAPIView(ListAPIView):
    queryset = Country.objects.all().annotate(
        geometry_empty=Func(F('geometry'), function='ST_IsEmpty', output_field=BooleanField()),
    ).filter(geometry_empty=False)
    serializer_class = BoundaryListCountrySerializer
    pagination_class = None

    @method_decorator(cache_page(timeout=settings.CACHES['default']['TIMEOUT']))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
