from django.urls import include, path

from rest_framework import routers

from proco.connection_statistics import api

app_name = 'connection_statistics'


router = routers.SimpleRouter()
router.register(r'realtime-connectivity', api.RealTimeConnectivityViewSet, basename='realtime')

urlpatterns = [
    path('global-stat/', api.GlobalStatsAPIView.as_view(), name='global-stat'),
    path('', include(router.urls)),
]
