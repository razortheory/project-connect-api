import csv
from datetime import datetime

from django.http import HttpResponse

from proco.locations.models import Country


class SchoolsCSVWriterBackend:
    def __init__(self, queryset, serializer_class, country_id):
        self.queryset = queryset
        self.serializer_class = serializer_class
        self.filename = self.get_filename(country_id)

    def get_filename(self, country_id):
        country_name = Country.objects.get(pk=country_id).name
        date = datetime.now().date().strftime('%Y-%m-%d')
        return f'{country_name}_schools_{date}.csv'

    def writeheader(self, writer, header, labels):
        header = dict(zip(header, labels))
        writer.writerow(header)

    def remove_underscore(self, field):
        return field.replace('_', ' ')

    def write(self):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{self.filename}"'

        serializer = self.serializer_class(
            self.queryset,
            many=True,
        )

        csv_header = self.serializer_class.Meta.fields
        labels = [self.remove_underscore(field.title()) for field in csv_header]
        writer = csv.DictWriter(response, fieldnames=csv_header)
        self.writeheader(writer, csv_header, labels)

        for row in serializer.data:
            writer.writerow(row)

        return response
