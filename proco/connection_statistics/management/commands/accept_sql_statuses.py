from django.core.management import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Accept raw sql.'

    def add_arguments(self, parser):
        parser.add_argument('sql_files_list', nargs='+', type=str)

    def handle(self, *args, **options):
        sql_files_list = options.get('sql_files_list')

        for sql_file in sql_files_list:
            with open(sql_file + '.sql', 'r') as sql:
                sql_commands = ' '.join(sql.readlines())
                cursor = connection.cursor()
                cursor.execute(sql_commands)
