from django.conf import settings
from django.db.models import Prefetch
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView

from django_filters.rest_framework import DjangoFilterBackend

from proco.connection_statistics.models import SchoolWeeklyStatus
from proco.locations.backends.csv import SchoolsCSVWriterBackend
from proco.locations.models import Country
from proco.schools.models import School
from proco.schools.serializers import (
    CSVSchoolsListSerializer,
    ListSchoolSerializer,
    SchoolPointSerializer,
    SchoolSerializer,
)


class SchoolsViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = School.objects.prefetch_related(
        Prefetch(
            'weekly_status',
            SchoolWeeklyStatus.objects.order_by('school_id', '-year', '-week').distinct('school_id'),
            to_attr='latest_status',
        ),
    )
    pagination_class = None
    serializer_class = SchoolSerializer
    filter_backends = (
        DjangoFilterBackend,
    )
    related_model = Country

    def get_queryset(self):
        return super().get_queryset().filter(country_id=self.kwargs['country_pk'])

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.action == 'list':
            serializer_class = ListSchoolSerializer
        if self.action == 'export_csv_schools':
            serializer_class = CSVSchoolsListSerializer
        return serializer_class

    @method_decorator(cache_page(timeout=settings.CACHES['default']['TIMEOUT']))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(methods=['get'], detail=False, url_path='export-csv-schools', url_name='export_csv_schools')
    def export_csv_schools(self, request, *args, **kwargs):
        country_id = self.kwargs['country_pk']
        queryset = self.get_queryset()
        serializer_class = self.get_serializer_class()
        csvwriter = SchoolsCSVWriterBackend(queryset, serializer_class, country_id)
        response = csvwriter.write()
        return response


class RandomSchoolsListAPIView(ListAPIView):
    queryset = School.objects.order_by('?')[:settings.RANDOM_SCHOOLS_DEFAULT_AMOUNT]
    serializer_class = SchoolPointSerializer
    pagination_class = None

    @method_decorator(cache_page(timeout=settings.CACHES['default']['TIMEOUT']))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
