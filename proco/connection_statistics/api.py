from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

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
