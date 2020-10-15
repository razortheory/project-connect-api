from django.core.management import BaseCommand
from django.utils import timezone

from proco.connection_statistics.tests.factories import (
    RealTimeConnectivityFactory,
    SchoolDailyStatusFactory,
    SchoolWeeklyStatusFactory,
)
from proco.schools.models import School
from proco.connection_statistics.models import RealTimeConnectivity
AREA_COEFF = 223.4267  # coefficient of the average number of schools per unit area (250к/USA area)

NUMBER_DAYS_WEEKLY_STATISTICS = 90
NUMBER_DAYS_DAILY_STATISTICS = 90
NUMBER_DAYS_REALTIME_STATISTICS = 30


class Command(BaseCommand):
    help = 'Generate sql for creating schools statuses.'

    def add_arguments(self, parser):
        parser.add_argument('country_id_list', nargs='+', type=int)

    def handle(self, *args, **options):
        country_id_list = options.get('country_id_list')

        for country_id in country_id_list:
            with open(f'{country_id}_statuses.sql', 'a') as file:
                realtime_list = []
                schools_daily_list = []
                schools_weekly_list = []
                realtime_count = 0
                schools_daily_count = 0
                schools_weekly_count = 0
                for idx, school in enumerate(School.objects.filter(country_id=country_id).iterator()):
                    if idx < 300000:
                        print('pass', idx)
                        continue
                    for day in range(NUMBER_DAYS_REALTIME_STATISTICS):
                        for hour in range(0, 20, 5):
                            date = timezone.now() - timezone.timedelta(days=day, hours=hour)
                            rt = RealTimeConnectivityFactory.build(school=school, created=date)
                            realtime_list.append(rt)
                            realtime_count += 1

                            if realtime_count % 5000 == 0:
                                query = """INSERT INTO connection_statistics_realtimeconnectivity (school_id, created,
                                        modified, connectivity_speed, connectivity_latency) VALUES """
                                for obj in realtime_list:
                                    query += f"""({obj.school.id}, '{obj.created}', '{obj.modified}',
                                                 {obj.connectivity_speed}, {obj.connectivity_latency}),"""
                                query = query[:-1] + ';'
                                file.write(query)
                                realtime_count = 0
                                realtime_list = []

                    for day in range(NUMBER_DAYS_DAILY_STATISTICS):
                        date = timezone.now() - timezone.timedelta(days=day)
                        sd = SchoolDailyStatusFactory.build(school=school, created=date, date=date)
                        schools_daily_list.append(sd)
                        schools_daily_count += 1

                        if schools_daily_count % 2000 == 0:
                            query = """INSERT INTO connection_statistics_schooldailystatus (school_id, created,
                                        modified, date, connectivity_speed, connectivity_latency) VALUES """
                            for obj in schools_daily_list:
                                query += f"""({obj.school.id}, '{obj.created}', '{obj.modified}', '{obj.date}',
                                            {obj.connectivity_speed}, {obj.connectivity_latency}),"""
                            query = query[:-1] + ';'
                            file.write(query)
                            schools_daily_count = 0
                            schools_daily_list = []

                    for day in range(0, NUMBER_DAYS_WEEKLY_STATISTICS, 7):
                        date = timezone.now() - timezone.timedelta(days=day)
                        year, week = date.isocalendar()[:2]
                        sw = SchoolWeeklyStatusFactory.build(school=school, year=year, week=week, date=date)
                        schools_weekly_list.append(sw)
                        schools_weekly_count += 1

                        if schools_weekly_count % 2000 == 0:
                            query = """INSERT INTO connection_statistics_schoolweeklystatus (school_id, created,
                                        modified, year, week, num_students, num_teachers, num_classroom,
                                        num_latrines, running_water, electricity_availability,
                                        computer_lab, num_computers, connectivity_type,
                                        connectivity_availability, connectivity, connectivity_status,
                                        connectivity_speed, connectivity_latency, date) VALUES """
                            for obj in schools_weekly_list:
                                query += f"""({obj.school.id}, '{obj.created}', '{obj.modified}', {obj.year},
                                         {obj.week}, {obj.num_students}, {obj.num_teachers}, {obj.num_classroom},
                                         {obj.num_latrines}, {obj.running_water}, {obj.electricity_availability},
                                         {obj.computer_lab}, {obj.num_computers}, '{obj.connectivity_type}',
                                         {obj.connectivity_availability}, {obj.connectivity},
                                         '{obj.connectivity_status}', {obj.connectivity_speed},
                                         {obj.connectivity_latency}, '{obj.date}'),"""
                            query = query[:-1] + ';'
                            file.write(query)
                            schools_weekly_count = 0
                            schools_weekly_list = []
                    print('added', school.name)

                if realtime_count:
                    query = """INSERT INTO connection_statistics_realtimeconnectivity (school_id, created,
                            modified, connectivity_speed, connectivity_latency) VALUES """
                    for obj in realtime_list:
                        query += f"""({obj.school.id}, '{obj.created}', '{obj.modified}',
                                     {obj.connectivity_speed}, {obj.connectivity_latency}),"""
                    query = query[:-1] + ';'
                    file.write(query)

                if schools_daily_count:
                    query = """INSERT INTO connection_statistics_schooldailystatus (school_id, created,
                                modified, date, connectivity_speed, connectivity_latency) VALUES """
                    for obj in schools_daily_list:
                        query += f"""({obj.school.id}, '{obj.created}', '{obj.modified}', '{obj.date}',
                                    {obj.connectivity_speed}, {obj.connectivity_latency}),"""
                    query = query[:-1] + ';'
                    file.write(query)

                if schools_weekly_count:
                    query = """INSERT INTO connection_statistics_schoolweeklystatus (school_id, created,
                                modified, year, week, num_students, num_teachers, num_classroom,
                                num_latrines, running_water, electricity_availability,
                                computer_lab, num_computers, connectivity_type,
                                connectivity_availability, connectivity, connectivity_status,
                                connectivity_speed, connectivity_latency, date) VALUES """
                    for obj in schools_weekly_list:
                        query += f"""({obj.school.id}, '{obj.created}', '{obj.modified}', {obj.year},
                                 {obj.week}, {obj.num_students}, {obj.num_teachers}, {obj.num_classroom},
                                 {obj.num_latrines}, {obj.running_water}, {obj.electricity_availability},
                                 {obj.computer_lab}, {obj.num_computers}, '{obj.connectivity_type}',
                                 {obj.connectivity_availability}, {obj.connectivity},
                                 '{obj.connectivity_status}', {obj.connectivity_speed},
                                 {obj.connectivity_latency}, '{obj.date}'),"""
                    query = query[:-1] + ';'
                    file.write(query)
