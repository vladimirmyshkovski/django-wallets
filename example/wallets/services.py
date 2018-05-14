import blockcypher
from django.contrib.auth import get_user_model
from .utils import get_wallet_model, get_api_key


def generate_new_address(user, coin_symbol):
    if isinstance(user, get_user_model()) and get_wallet_model(coin_symbol):
        r = blockcypher.generate_new_address(
            coin_symbol=coin_symbol,
            api_key=get_api_key()
        )
        obj = get_wallet_model(coin_symbol).objects.create(
            user=user,
            private=r['private'],
            public=r['public'],
            address=r['address'],
            wif=r['wif']
        )
        return obj
    else:
        return None
