from django.apps import AppConfig


class AplikaceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'aplikace'

    def ready(self):
        import aplikace.signals  # noqa
