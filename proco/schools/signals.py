from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from proco.connection_statistics.models import CountryWeeklyStatus
from proco.schools.models import School


@receiver(post_save, sender=School)
def change_integration_status_country(instance, created=False, **kwargs):
    country_weekly = CountryWeeklyStatus.objects.filter(country_id=instance.country.id).last()
    year, week, weekday = timezone.now().isocalendar()
    if not (country_weekly.year == year and country_weekly.week == week):
        country_weekly.id = None
        country_weekly.year = year
        country_weekly.week = week

    if instance.geopoint:
        if country_weekly.integration_status == CountryWeeklyStatus.JOINED:
            country_weekly.integration_status = CountryWeeklyStatus.SCHOOL_MAPPED

    country_weekly.save()

    if created:
        country_weekly.schools_total = F('schools_total') + 1
        country_weekly.schools_connectivity_unknown = F('schools_connectivity_unknown') + 1

        country_weekly.save(update_fields=('schools_total', 'schools_connectivity_unknown'))
