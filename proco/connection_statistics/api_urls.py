from django.urls import path

from proco.connection_statistics import api

app_name = 'connection_statistics'

urlpatterns = [
    path('global-stat/', api.GlobalStatsAPIView.as_view(), name='global-stat'),
]
