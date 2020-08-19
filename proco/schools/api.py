from rest_framework import mixins, viewsets

from django_filters.rest_framework import DjangoFilterBackend

from proco.schools.models import School
from proco.schools.serializers import SchoolSerializer


class SchoolsViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    filter_backends = (
        DjangoFilterBackend,
    )

    def get_queryset(self):
        return self.queryset.filter(country_id=self.kwargs['country_id'])
