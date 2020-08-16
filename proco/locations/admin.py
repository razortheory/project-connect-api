from django.contrib import admin

from proco.locations.models import Country, Location
from proco.utils.admin import CountryNameDisplayAdminMixin


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('flag_preview', 'name', 'code', 'location_preview')
    search_fields = ('name',)
    list_display_links = ('flag_preview', 'name', 'location_preview')

    def flag_preview(self, obj):
        if not obj.flag:
            return ''
        return f'<img src="{obj.flag.url}" style="max-width:50px; max-height:50px;" />'

    flag_preview.short_description = 'Flag'

    def location_preview(self, obj):
        if not obj.map_preview:
            return ''
        return f'<img src="{obj.map_preview.url}" style="max-width:100px; max-height:100px;" />'

    location_preview.short_description = 'Map Preview'


@admin.register(Location)
class LocationAdmin(CountryNameDisplayAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'get_country_name')
    list_select_related = ('country', 'parent')
    search_fields = ('name', 'country__name')
