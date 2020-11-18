from datetime import datetime

from django.http import Http404

from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.utils.urls import remove_query_param
from rest_framework.views import APIView

from django_filters.rest_framework import DjangoFilterBackend

from proco.connection_statistics.filters import DateMonthFilter, DateWeekNumberFilter, DateYearFilter
from proco.connection_statistics.models import (
    CountryDailyStatus,
    CountryWeeklyStatus,
    SchoolDailyStatus,
    SchoolWeeklyStatus,
)
from proco.connection_statistics.serializers import (
    CountryDailyStatusSerializer,
    CountryWeeklyStatusSerializer,
    SchoolDailyStatusSerializer,
)
from proco.locations.models import Country
from proco.schools.models import School
from proco.utils.cache import cache_manager


class GlobalStatsAPIView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        def calculate_global_statistic():
            schools_qs = School.objects.all()
            countries_statuses_aggregated = Country.objects.aggregate_integration_statuses()
            total_schools = schools_qs.count()
            schools_mapped = schools_qs.filter(geopoint__isnull=False).count()
            schools_without_connectivity = schools_qs.filter(
                last_weekly_status__connectivity_status=SchoolWeeklyStatus.CONNECTIVITY_STATUSES.no,
            ).count()
            percent_schools_without_connectivity = schools_without_connectivity / total_schools
            last_date_updated = CountryWeeklyStatus.objects.all().order_by('-date').first().date

            data = {
                'total_schools': total_schools,
                'schools_mapped': schools_mapped,
                'percent_schools_without_connectivity': percent_schools_without_connectivity,
                'countries_joined': countries_statuses_aggregated['countries_joined'],
                'countries_connected_to_realtime': countries_statuses_aggregated['countries_connected_to_realtime'],
                'countries_with_static_data': countries_statuses_aggregated['countries_with_static_data'],
                'last_date_updated': last_date_updated.strftime('%B %Y'),
            }
            return data

        request_path = remove_query_param(request.get_full_path(), 'cache')
        if not request.query_params.get('cache', 'on').lower() in ['on', 'true']:
            data = calculate_global_statistic()
            cache_manager.set('GLOBAL_STATS', data, request_path=request_path)
        else:
            data = cache_manager.get('GLOBAL_STATS')
            if not data:
                data = calculate_global_statistic()
                cache_manager.set('GLOBAL_STATS', data, request_path=request_path)

        return Response(data=data)


class CountryWeekStatsAPIView(RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CountryWeeklyStatusSerializer

    def get_object(self, *args, **kwargs):
        week = self.kwargs['week']
        year = self.kwargs['year']
        date = datetime.strptime(f'{year}-W{week}-1', '%Y-W%W-%w')
        instance = CountryWeeklyStatus.objects.filter(country_id=self.kwargs['country_id'], date__lte=date).last()

        if not instance:
            raise Http404

        return instance


class CountryDailyStatsListAPIView(ListAPIView):
    model = CountryDailyStatus
    queryset = model.objects.all()
    serializer_class = CountryDailyStatusSerializer
    filter_backends = (
        DjangoFilterBackend,
        DateYearFilter,
        DateWeekNumberFilter,
    )
    filterset_fields = {
        'date': ['lte', 'gte'],
    }

    def get_queryset(self):
        queryset = super(CountryDailyStatsListAPIView, self).get_queryset()
        return queryset.filter(country_id=self.kwargs['country_id'])


class SchoolDailyStatsListAPIView(ListAPIView):
    model = SchoolDailyStatus
    queryset = model.objects.all()
    serializer_class = SchoolDailyStatusSerializer
    filter_backends = (
        DjangoFilterBackend,
        DateYearFilter,
        DateWeekNumberFilter,
        DateMonthFilter,
    )
    filterset_fields = {
        'date': ['lte', 'gte'],
    }

    def get_queryset(self):
        queryset = super(SchoolDailyStatsListAPIView, self).get_queryset()
        return queryset.filter(school_id=self.kwargs['school_id'])
