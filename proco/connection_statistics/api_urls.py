from django.urls import path

from proco.connection_statistics import api

app_name = 'connection_statistics'

urlpatterns = [
    path('global-stat/', api.GlobalStatsAPIView.as_view(), name='global-stat'),
    path('country/<int:country_id>/daily-stat/', api.CountryDailyStatsListAPIView.as_view(), name='country-daily-stat'),
    path(
        'country/<int:country_id>/weekly-stat/<int:week>/<int:year>/',
        api.CountryWeekStatsAPIView.as_view(),
        name='country-weekly-stat'
    ),
]
