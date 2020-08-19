from django.urls import include, path

from rest_framework import routers

from proco.schools import api

router = routers.SimpleRouter()
router.register(r'country//(?P<country_id>[0-9]+)/schools', api.SchoolsViewSet, basename='schools')


app_name = 'schools'

urlpatterns = [
    path('', include(router.urls)),
]
