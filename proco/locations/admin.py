from django.contrib import admin
from django.utils.safestring import mark_safe

from proco.locations.models import Country, Location
from proco.utils.admin import CountryNameDisplayAdminMixin


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'flag_preview', 'location_preview')
    search_fields = ('name',)
    exclude = ('geometry_simplified',)

    def flag_preview(self, obj):
        if not obj.flag:
            return ''
        return mark_safe(f'<img src="{obj.flag.url}" style="max-width:50px; max-height:50px;" />')
    flag_preview.short_description = 'Flag'

    def location_preview(self, obj):
        if not obj.map_preview:
            return ''
        return mark_safe(f'<img src="{obj.map_preview.url}" style="max-width:100px; max-height:100px;" />')
    location_preview.short_description = 'Map Preview'


@admin.register(Location)
class LocationAdmin(CountryNameDisplayAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'get_country_name')
    list_select_related = ('country', 'parent')
    search_fields = ('name', 'country__name')
    exclude = ('geometry_simplified',)
