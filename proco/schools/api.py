from rest_framework import mixins, viewsets

from django_filters.rest_framework import DjangoFilterBackend

from proco.locations.models import Country
from proco.schools.models import School
from proco.schools.serializers import ListSchoolSerializer, SchoolSerializer


class SchoolsViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = SchoolSerializer
    filter_backends = (
        DjangoFilterBackend,
    )
    related_model = Country

    def get_queryset(self):
        return School.objects.filter(country_id=self.kwargs['country_pk'])

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.action == 'list':
            serializer_class = ListSchoolSerializer
        return serializer_class