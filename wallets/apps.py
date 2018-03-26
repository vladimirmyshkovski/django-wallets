from django.apps import AppConfig


class WalletsConfig(AppConfig):
    name = 'adamsmen.wallets'
    verbose_name = 'Wallets'

    def ready(self):
    	import adamsmen.wallets.signals
