from django.shortcuts import get_object_or_404

from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from django_filters.rest_framework import DjangoFilterBackend

from proco.connection_statistics.models import CountryDailyStatus, CountryWeeklyStatus
from proco.connection_statistics.serializers import CountryDailyStatusSerializer, CountryWeeklyStatusSerializer
from proco.locations.models import Country
from proco.schools.models import School


class GlobalStatsAPIView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        countries_joined = Country.objects.count()
        schools_qs = School.objects.annotate_status_connectivity()
        total_schools = schools_qs.count()
        schools_mapped = schools_qs.filter(geopoint__isnull=False).count()
        schools_without_connectivity = schools_qs.filter(connectivity=False).count()
        percent_schools_without_connectivity = schools_without_connectivity / total_schools * 100

        data = {
            'total_schools': total_schools,
            'schools_mapped': schools_mapped,
            'percent_schools_without_connectivity': percent_schools_without_connectivity,
            'countries_joined': countries_joined,
        }
        return Response(data=data)


class CountryWeekStatsAPIView(RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CountryWeeklyStatusSerializer

    def get_object(self, *args, **kwargs):
        instance = get_object_or_404(
            CountryWeeklyStatus, country_id=self.kwargs['country_id'],
            week=self.kwargs['week'], year=self.kwargs['year'],
        )
        return instance


class CountryDailyStatsListAPIView(ListAPIView):
    model = CountryDailyStatus
    queryset = model.objects.all()
    serializer_class = CountryDailyStatusSerializer
    filter_backends = (
        DjangoFilterBackend,
    )
    filterset_fields = ['year', 'week']

    def get_queryset(self):
        queryset = super(CountryDailyStatsListAPIView, self).get_queryset()
        queryset = queryset.filter(country_id=self.kwargs['country_id'])
        return queryset.aggregate_daily_stats()
