from django.contrib import admin, messages
from django.contrib.admin.options import csrf_protect_m
from django.contrib.gis.db.models import PointField
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils.safestring import mark_safe

from mapbox_location_field.admin import MapAdmin
from mapbox_location_field.widgets import MapAdminInput

from proco.locations.filters import CountryFilterList
from proco.schools.forms import ImportSchoolsCSVForm
from proco.schools.models import FileImport, School
from proco.schools.tasks import process_loaded_file
from proco.utils.admin import CountryNameDisplayAdminMixin


@admin.register(School)
class SchoolAdmin(CountryNameDisplayAdminMixin, MapAdmin):
    formfield_overrides = {
        PointField: {'widget': MapAdminInput},
    }
    list_display = ('name', 'get_country_name', 'address', 'education_level', 'school_type')
    list_filter = (CountryFilterList, 'education_level', 'environment', 'school_type')
    search_fields = ('name', 'country__name', 'location__name')
    change_list_template = 'admin/schools/change_list.html'
    ordering = ('country', 'name')
    readonly_fields = ('get_weekly_stats_url',)
    raw_id_fields = ('country', 'location')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import/csv/', self.import_csv, name='schools_school_import_csv'),
        ]
        return custom_urls + urls

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(country__in=request.user.countries_available.all())
        return qs.prefetch_related('country').defer('location')

    def import_csv(self, request):
        if request.method == 'GET':
            form = ImportSchoolsCSVForm()
        else:
            form = ImportSchoolsCSVForm(data=request.POST, files=request.FILES)
            if form.is_valid():
                cleaned_data = form.clean()
                imported_file = FileImport.objects.create(
                    uploaded_file=cleaned_data['csv_file'], uploaded_by=request.user,
                )
                process_loaded_file.delay(imported_file.id, force=cleaned_data['force'])

                messages.success(request, 'Your file was uploaded and will be processed soon.')
                return redirect('admin:schools_fileimport_change', imported_file.id)

        return render(request, 'admin/schools/import_csv.html', {'form': form})

    @csrf_protect_m
    def changelist_view(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}

        extra_context['import_form'] = ImportSchoolsCSVForm()

        return super(SchoolAdmin, self).changelist_view(request, extra_context)

    def get_weekly_stats_url(self, obj):
        stats_url = reverse('admin:connection_statistics_schoolweeklystatus_changelist')
        return mark_safe(f'<a href="{stats_url}?school={obj.id}" target="_blank">Here</a>')  # noqa: S703,S308

    get_weekly_stats_url.short_description = 'Weekly Stats'


@admin.register(FileImport)
class FileImportAdmin(admin.ModelAdmin):
    change_form_template = 'admin/schools/file_imports_change_form.html'

    list_display = ('id', 'uploaded_file', 'status', 'uploaded_by', 'modified')
    list_select_related = ('uploaded_by',)
    list_filter = ('status',)
    readonly_fields = ('status', 'errors', 'uploaded_by', 'modified')
    ordering = ('-id',)

    def has_add_permission(self, request):
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(uploaded_by=request.user)
        return qs
