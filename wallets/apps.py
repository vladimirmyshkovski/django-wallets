from django.apps import AppConfig


class WalletsConfig(AppConfig):
    name = 'wallets'
    verbose_name = 'Wallets'

    def ready(self):
        from . import signals
        from . import models
        models.Invoice.receiver_wallet_object.add_relation(models.Btc)
        models.Invoice.receiver_wallet_object.add_relation(models.Ltc)
        models.Invoice.receiver_wallet_object.add_relation(models.Dash)
        models.Invoice.receiver_wallet_object.add_relation(models.Doge)
        models.Invoice.receiver_wallet_object.add_relation(models.Bcy)
