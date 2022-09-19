from django.apps import AppConfig
import os

class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    def ready(self):
        from . import jobs

        if os.environ.get('RUN_MAIN', None) != 'true':
            jobs.start()
            # jobs.test()