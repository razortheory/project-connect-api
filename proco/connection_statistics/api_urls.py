from django.urls import path

from proco.connection_statistics import api

app_name = 'connection_statistics'

urlpatterns = [
    path('global-stat/', api.GlobalStatsAPIView.as_view(), name='global-stat'),
    path('country/<str:country_id>/daily-stat/', api.CountryDailyStatsListAPIView.as_view(), name='country-daily-stat'),
    path('school/<int:school_id>/daily-stat/', api.SchoolDailyStatsListAPIView.as_view(), name='school-daily-stat'),
    path(
        'country/<str:country_id>/weekly-stat/<int:year>/<int:week>/',
        api.CountryWeekStatsAPIView.as_view(),
        name='country-weekly-stat',
    ),
]
