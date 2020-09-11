from django.db import models
from django.db.models import Case, Count, IntegerField, When


class CountryWeeklyStatusManager(models.Manager):
    def aggregate_integration_statuses(self):
        from proco.connection_statistics.models import CountryWeeklyStatus
        return self.get_queryset().aggregate(
            countries_connected_to_realtime=Count(Case(When(
                integration_status=CountryWeeklyStatus.REALTIME_MAPPED, then=1),
                output_field=IntegerField())),
            countries_with_static_data=Count(Case(When(
                integration_status=CountryWeeklyStatus.STATIC_MAPPED, then=1),
                output_field=IntegerField()),
            ),
        )
