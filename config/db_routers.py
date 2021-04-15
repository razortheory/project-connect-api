class DBRouter(object):
    def db_for_read(self, model, **hints):
        if model._meta.app_label in ('sites', 'contenttypes', 'auth'):
            return None

        if model._meta.app_label == 'realtime_unicef':
            return 'realtime'
        return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.app_label in ('sites', 'contenttypes', 'auth'):
            return None

        if model._meta.app_label == 'realtime_unicef':
            return 'realtime'
        return 'default'

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in ('sites', 'contenttypes', 'auth'):
            return True

        return db == 'default'
