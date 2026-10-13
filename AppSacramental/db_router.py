class AgendaRouter:

    def db_for_read(self, model, **hints):
        app_label = model._meta.app_label

        if app_label == "agenda":
            return "agenda"

        if app_label == "historial":
            return "historial"

        return "default"

    def db_for_write(self, model, **hints):
        app_label = model._meta.app_label

        if app_label == "agenda":
            return "agenda"

        if app_label == "historial":
            return "historial"

        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        db1 = obj1._state.db
        db2 = obj2._state.db

        if db1 and db2 and db1 != db2:
            return False

        return None

    def allow_migrate(
        self,
        db,
        app_label,
        model_name=None,
        **hints
    ):
        if app_label == "agenda":
            return db == "agenda"

        if app_label == "historial":
            return db == "historial"

        return db == "default"