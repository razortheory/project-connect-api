from django.contrib import admin

from proco.schools.models import School
from proco.utils.admin import CountryNameDisplayAdminMixin, LocationNameDisplayAdminMixin


@admin.register(School)
class SchoolAdmin(LocationNameDisplayAdminMixin, CountryNameDisplayAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'get_country_name', 'get_location_name', 'address', 'postal_code',
                    'education_level', 'environment', 'school_type')
    list_select_related = ('country', 'location')
    list_filter = ('education_level', 'environment', 'school_type')
    search_fields = ('name', 'country__name', 'location__name')
