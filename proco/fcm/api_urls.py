from django.urls import include, path

from rest_framework import routers

from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet

router = routers.SimpleRouter()
router.register('devices', FCMDeviceAuthorizedViewSet)

app_name = 'fcm'

urlpatterns = [
    path('', include(router.urls)),
]
