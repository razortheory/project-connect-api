from django.contrib import admin
from django.contrib.gis.admin import GeoModelAdmin
from django.utils.safestring import mark_safe

from proco.locations.filters import CountryFilterList
from proco.locations.models import Country, Location
from proco.utils.admin import CountryNameDisplayAdminMixin


@admin.register(Country)
class CountryAdmin(GeoModelAdmin):
    modifiable = False

    list_display = ('name', 'code', 'flag_preview')
    search_fields = ('name',)
    exclude = ('geometry_simplified',)
    raw_id_fields = ('last_weekly_status',)

    def flag_preview(self, obj):
        if not obj.flag:
            return ''
        return mark_safe(f'<img src="{obj.flag.url}" style="max-width:50px; max-height:50px;" />')  # noqa: S703,S308

    flag_preview.short_description = 'Flag'

    def get_queryset(self, request):
        return super().get_queryset(request).defer('geometry', 'geometry_simplified')


@admin.register(Location)
class LocationAdmin(CountryNameDisplayAdminMixin, GeoModelAdmin):
    modifiable = False
    show_full_result_count = False

    list_display = ('name', 'get_country_name')
    list_filter = (CountryFilterList,)
    search_fields = ('name', 'country__name')
    exclude = ('geometry_simplified',)
    raw_id_fields = ('parent', 'country')

    def get_queryset(self, request):
        return Location._base_manager.defer(
            'geometry', 'geometry_simplified',
        ).order_by(
            Location.objects.tree_id_attr, Location.objects.left_attr,
        ).prefetch_related('country')
