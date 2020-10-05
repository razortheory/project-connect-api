from django.contrib import admin
from django.utils.safestring import mark_safe

from proco.locations.filters import CountryFilterList
from proco.locations.models import Country, Location
from proco.utils.admin import CountryNameDisplayAdminMixin


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'flag_preview')
    search_fields = ('name',)
    exclude = ('geometry_simplified',)

    def flag_preview(self, obj):
        if not obj.flag:
            return ''
        return mark_safe(f'<img src="{obj.flag.url}" style="max-width:50px; max-height:50px;" />')  # noqa: S703,S308

    flag_preview.short_description = 'Flag'


@admin.register(Location)
class LocationAdmin(CountryNameDisplayAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'get_country_name')
    list_filter = (CountryFilterList,)
    search_fields = ('name', 'country__name')
    exclude = ('geometry_simplified',)
    raw_id_fields = ('parent', 'country')

    def get_queryset(self, *args, **kwargs):
        qs = super(LocationAdmin, self).get_queryset(*args, **kwargs).defer('geometry', 'geometry_simplified')
        return qs
