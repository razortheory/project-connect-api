from django.db import connections, models


class ApproxQuerySet(models.QuerySet):
    def count(self, approx=True):
        if approx and not self.query.where:
            cursor = connections[self.db].cursor()
            cursor.execute(
                'SELECT reltuples::int FROM pg_class WHERE relname = %s;',
                (self.model._meta.db_table,),
            )
            return cursor.fetchall()[0][0]
        else:
            return super().count()
