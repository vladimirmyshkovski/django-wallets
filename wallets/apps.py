from django.apps import AppConfig
import environ


env = environ.Env()


class WalletsConfig(AppConfig):
    name = 'wallets'
    verbose_name = 'Wallets'

    def ready(self):
        from .models import ApiKey
        api_key = env('DEFAULT_BLOCKCYPHER_API_KEY')
        try:
            ApiKey.objects.get_or_create(api_key=api_key)
        except Exception:
            pass
