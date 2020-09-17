from django.contrib import admin

from proco.connection_statistics.models import (
    CountryDailyStatus,
    CountryWeeklyStatus,
    RealTimeConnectivity,
    SchoolDailyStatus,
    SchoolWeeklyStatus,
)
from proco.utils.admin import CountryNameDisplayAdminMixin, SchoolNameDisplayAdminMixin


@admin.register(CountryWeeklyStatus)
class CountryWeeklyStatusAdmin(CountryNameDisplayAdminMixin, admin.ModelAdmin):
    list_display = ('get_country_name', 'year', 'week', 'integration_status', 'connectivity_speed', 'schools_total',
                    'schools_connected', 'schools_connectivity_unknown', 'schools_connectivity_no',
                    'schools_connectivity_moderate', 'schools_connectivity_good')
    list_filter = ('integration_status', 'country__name')
    list_select_related = ('country',)
    search_fields = ('country__name', 'year', 'week')
    ordering = ('-id',)
    readonly_fields = ('year', 'week', 'integration_status')

    def has_change_permission(self, request, obj=None):
        perm = super().has_change_permission(request, obj)
        if not request.user.is_superuser and obj:
            perm = obj.country in request.user.countries_available.all()
        return perm


@admin.register(SchoolWeeklyStatus)
class SchoolWeeklyStatusAdmin(SchoolNameDisplayAdminMixin, admin.ModelAdmin):
    list_display = ('get_school_name', 'year', 'week', 'connectivity_status', 'connectivity_type', 'connectivity_speed',
                    'connectivity_latency', 'num_students', 'num_teachers')
    list_select_related = ('school',)
    search_fields = ('school__name', 'year', 'week')
    ordering = ('-id',)
    readonly_fields = ('year', 'week')
    raw_id_fields = ('school',)


@admin.register(CountryDailyStatus)
class CountryDailyStatusAdmin(CountryNameDisplayAdminMixin, admin.ModelAdmin):
    list_display = ('get_country_name', 'date', 'connectivity_speed', 'connectivity_latency')
    list_select_related = ('country',)
    search_fields = ('country__name',)
    ordering = ('-id',)
    date_hierarchy = 'date'


@admin.register(SchoolDailyStatus)
class SchoolDailyStatusAdmin(SchoolNameDisplayAdminMixin, admin.ModelAdmin):
    list_display = ('get_school_name', 'date', 'connectivity_speed', 'connectivity_latency')
    list_select_related = ('school',)
    search_fields = ('school__name',)
    ordering = ('-id',)
    raw_id_fields = ('school',)
    date_hierarchy = 'date'


@admin.register(RealTimeConnectivity)
class RealTimeConnectivityAdmin(SchoolNameDisplayAdminMixin, admin.ModelAdmin):
    list_display = ('get_school_name', 'created', 'connectivity_speed', 'connectivity_latency')
    list_select_related = ('school',)
    search_fields = ('school__name',)
    ordering = ('-id',)
    readonly_fields = ('created', 'modified')
