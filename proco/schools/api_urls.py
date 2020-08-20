from django.urls import include, path

from rest_framework_nested import routers

from proco.locations.api_urls import router as location_router
from proco.schools import api

country_schools = routers.NestedSimpleRouter(location_router, r'countries', lookup='country')
country_schools.register(r'schools', api.SchoolsViewSet, basename='schools')

app_name = 'schools'

urlpatterns = [
    path('', include(country_schools.urls)),
]