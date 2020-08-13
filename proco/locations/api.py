from rest_framework import mixins, viewsets
from rest_framework.filters import OrderingFilter

from proco.locations.models import Country
from proco.locations.serializers import CountrySerializer


class CountryViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    filter_backends = (
        OrderingFilter,
    )
    ordering = ('name',)
    ordering_fields = ('name',)
