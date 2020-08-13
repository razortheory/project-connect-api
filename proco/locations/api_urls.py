from django.urls import include, path

from rest_framework import routers

from proco.locations import api

router = routers.SimpleRouter()
router.register(r'countries', api.CountryViewSet, basename='countries')


app_name = 'locations'

urlpatterns = [
    path('', include(router.urls)),
]
