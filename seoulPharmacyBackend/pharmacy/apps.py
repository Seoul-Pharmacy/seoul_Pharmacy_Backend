import os

from django.apps import AppConfig


class PharmacyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pharmacy'

    def ready(self):
        if os.environ.get('RUN_MAIN', None) is not None:
            from .operator import main
            main()
