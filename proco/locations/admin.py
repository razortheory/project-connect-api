from django.contrib import admin

from proco.locations.models import Country


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    pass
