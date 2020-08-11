from django.utils import timezone


def get_current_year():
    return timezone.now().year


def get_current_week():
    return timezone.now().strftime('%U')


def get_current_weekday():
    return timezone.now().weekday()
