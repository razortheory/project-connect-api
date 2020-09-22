import csv
from datetime import datetime

from django.conf import settings
from django.db.models import Prefetch
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework import mixins, viewsets
from rest_framework.generics import ListAPIView
from rest_framework.mixins import ListModelMixin

from django_filters.rest_framework import DjangoFilterBackend

from proco.connection_statistics.models import SchoolWeeklyStatus
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
        return serializer_class

    @method_decorator(cache_page(timeout=settings.CACHES['default']['TIMEOUT']))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class RandomSchoolsListAPIView(ListAPIView):
    queryset = School.objects.order_by('?')[:settings.RANDOM_SCHOOLS_DEFAULT_AMOUNT]
    serializer_class = SchoolPointSerializer
    pagination_class = None

    @method_decorator(cache_page(timeout=settings.CACHES['default']['TIMEOUT']))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CSVExportSchoolsListViewSet(ListModelMixin, viewsets.GenericViewSet):
    serializer_class = CSVSchoolsListSerializer

    def get_queryset(self):
        queryset = School.objects.filter(country_id=self.kwargs['country_pk']).prefetch_related(
            Prefetch(
                'weekly_status',
                SchoolWeeklyStatus.objects.order_by('school_id', '-year', '-week').distinct('school_id'),
                to_attr='latest_status',
            ),
        )
        return queryset

    def get_filename(self):
        country_name = Country.objects.get(pk=self.kwargs['country_pk']).name
        date = datetime.now().date().strftime('%Y-%m-%d')
        return f'{country_name}_schools_{date}.csv'

    def writeheader(self, writer, header, labels):
        header = dict(zip(header, labels))
        writer.writerow(header)

    def remove_underscore(self, field):
        return field.replace('_', ' ')

    def list(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        filename = self.get_filename()
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        serializer = self.serializer_class(
            self.get_queryset(),
            many=True,
        )

        csv_header = self.serializer_class.Meta.fields
        labels = [self.remove_underscore(field.title()) for field in csv_header]
        writer = csv.DictWriter(response, fieldnames=csv_header)
        self.writeheader(writer, csv_header, labels)

        for row in serializer.data:
            writer.writerow(row)

        return response
