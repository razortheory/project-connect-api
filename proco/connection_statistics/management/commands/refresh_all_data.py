from django.core.management import BaseCommand

from proco.connection_statistics.models import RealTimeConnectivity, SchoolDailyStatus, SchoolWeeklyStatus


class Command(BaseCommand):
    help = 'Generate sql for creating schools statuses.'

    def add_arguments(self, parser):
        parser.add_argument('country_id_list', nargs='+', type=int)

    def handle(self, *args, **options):
        country_id_list = options.get('country_id_list')

        for country_id in country_id_list:
            print('-start')
            RealTimeConnectivity.objects.filter(school__country_id=country_id).delete()
            print('realtime clear')
            SchoolDailyStatus.objects.filter(school__country_id=country_id).delete()
            print('daily clear')
            SchoolWeeklyStatus.objects.filter(school__country_id=country_id).delete()
            print('weekly clear')
