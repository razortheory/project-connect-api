from django.urls import include, path

from rest_framework_nested import routers

from proco.locations.api_urls import router as location_router
from proco.schools import api

country_schools = routers.NestedSimpleRouter(location_router, r'countries', lookup='country')
country_schools.register(r'schools', api.SchoolsViewSet, basename='schools')
country_schools.register(r'export-csv-schools', api.CSVExportSchoolsListViewSet, basename='export_csv_schools')


app_name = 'schools'

urlpatterns = [
    path('', include(country_schools.urls)),
    path('schools/random/', api.RandomSchoolsListAPIView.as_view(), name='random-schools'),
    # path('export-csv-schools/', api.CSVExportSchoolsListView.as_view(), name='export-schools-csv')
]
