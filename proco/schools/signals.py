from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from proco.connection_statistics.models import CountryWeeklyStatus
from proco.schools.models import School


@receiver(post_save, sender=School)
def change_integration_status_country(instance, created=False, **kwargs):
    if instance.geopoint:
        country_weekly = CountryWeeklyStatus.objects.filter(country_id=instance.country.id).last()
        if country_weekly.integration_status == CountryWeeklyStatus.JOINED:
            year, week, weekday = timezone.now().isocalendar()
            if not (country_weekly.year == year and country_weekly.week == week):
                country_weekly.id = None
            country_weekly.integration_status = CountryWeeklyStatus.SCHOOL_MAPPED
            country_weekly.save()
            country_weekly.reset_date_fields()
