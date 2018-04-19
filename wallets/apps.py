from django.apps import AppConfig


class WalletsConfig(AppConfig):
    name = 'wallets'
    verbose_name = 'Wallets'

    def ready(self):
    	from . import signals
