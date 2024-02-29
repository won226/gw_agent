import os

from django.apps import AppConfig
from . import operator

class ClusterConfig(AppConfig):
    default_auto_field = 'django.db.models.AutoField'
    name = 'cluster'

    def ready(self):
        # Below code help to initialize gedge-agent object only once
        if not os.environ.get('APP'):
            os.environ['APP'] = 'True'
        else:
            operator.start()
