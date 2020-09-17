from django.conf import settings
from django.db.models import Prefetch
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework import mixins, viewsets
from rest_framework.generics import ListAPIView

from django_filters.rest_framework import DjangoFilterBackend

from proco.connection_statistics.models import SchoolWeeklyStatus
from proco.locations.models import Country
from proco.schools.models import School
from proco.schools.serializers import ListSchoolSerializer, SchoolPointSerializer, SchoolSerializer


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
