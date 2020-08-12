from django.contrib import admin, messages
from django.shortcuts import redirect, render
from django.urls import path

from proco.schools.forms import ImportSchoolsCSVForm
from proco.schools.loaders import csv as csv_loader, ingest
from proco.schools.models import School


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    change_list_template = 'admin/schools/change_list.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import/csv/', self.import_csv, name='schools_school_import_csv')
        ]
        return custom_urls + urls

    def import_csv(self, request):
        if request.method == 'GET':
            form = ImportSchoolsCSVForm()
        else:
            form = ImportSchoolsCSVForm(data=request.POST, files=request.FILES)
            if form.is_valid():
                cleaned_data = form.clean()
                # todo: fail if something wrong
                ingest.save_data(
                    cleaned_data['country'], csv_loader.load_file(cleaned_data['csv_file']),
                    skip_errors=True
                )

                messages.success(request, 'Completed')
                return redirect('admin:schools_school_changelist')

        return render(request, 'admin/schools/import_csv.html', {'form': form})
