from django.contrib import admin, messages
from django.shortcuts import redirect, render
from django.urls import path

from proco.schools.forms import ImportSchoolsCSVForm
from proco.schools.models import FileImport, School
from proco.schools.tasks import process_loaded_file


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    change_list_template = 'admin/schools/change_list.html'
    ordering = ('country', 'name')
    search_fields = ('name',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import/csv/', self.import_csv, name='schools_school_import_csv'),
        ]
        return custom_urls + urls

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
                process_loaded_file.delay(cleaned_data['country'].id, imported_file.id)

                messages.success(request, 'Your file was uploaded and will be processed soon.')
                return redirect('admin:schools_fileimport_change', imported_file.id)

        return render(request, 'admin/schools/import_csv.html', {'form': form})


@admin.register(FileImport)
class FileImportAdmin(admin.ModelAdmin):
    list_display = ('id', 'uploaded_file', 'status')
    list_filter = ('status',)
    readonly_fields = ('status', 'errors')
    ordering = ('-id',)
