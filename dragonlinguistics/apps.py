from django.apps import AppConfig


class DragonLinguisticsConfig(AppConfig):
    name = 'dragonlinguistics'
    verbose_name = 'Dragon Linguistics'

    def ready(self):
        from . import signals
