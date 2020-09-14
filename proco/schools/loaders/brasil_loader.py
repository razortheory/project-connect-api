from django.contrib.gis.geos import Point
from django.utils import timezone

import requests

from proco.connection_statistics.models import SchoolDailyStatus
from proco.locations.models import Country
from proco.schools.models import School


class BrasilSimnetLoader(object):
    base_url = "https://api.simet.nic.br/"

    def __init__(self):
        self.country = Country.objects.get(code="BR")

    def load_schools(self):
        response = requests.get("{0}school-measures/v1/getSchools".format(self.base_url))
        return response.json()

    def save_school(self, school_data):
        required_fields = set(["LNG", "LAT", "CO_ENTIDADE", "NO_ENTIDADE"])

        if required_fields - set(school_data.keys()) == set():
            School.objects.update_or_create(
                external_id=school_data["CO_ENTIDADE"],
                country=self.country,
                defaults={
                    'name': school_data["NO_ENTIDADE"],
                    'geopoint': Point(x=school_data["LNG"], y=school_data["LAT"]),
                    'admin_1_name': school_data.get("NM_ESTADO", ''),
                    'admin_4_name': school_data.get("NM_MUNICIP", ''),
                },
            )


    def update_schools(self):
        schools = self.load_schools()

        for school in schools:
            self.save_school(school)

    def load_schools_statistic(self, date):
        response = requests.get(
            "{0}school-measures/v1/getMeasuresbyDayofYear?dayofyear={1}".format(self.base_url, date),
        )
        return response.json()

    def update_statistic(self, date=None):
        if date == None:
            date = timezone.now().date()

        statistic = self.load_schools_statistic(date)

        statistic_batch = []
        for data in statistic:
            if 'school_code' in data:
                school = School.objects.filter(external_id=data['school_code']).first()

                if school:
                    daily_statistic = SchoolDailyStatus(
                        date=date, school=school,
                        connectivity_speed=data.get('tcp_down_median_mbps', None),
                        connectivity_latency=data.get('rtt_median_ms', None),
                    )
                    statistic_batch.append(daily_statistic)

                if len(statistic_batch) == 5000:
                    SchoolDailyStatus.objects.bulk_create(statistic_batch)
                    statistic_batch = []

        if len(statistic_batch) > 0:
            SchoolDailyStatus.objects.bulk_create(statistic_batch)


brasil_statistic_loader = BrasilSimnetLoader()
