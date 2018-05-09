import environ
import logging
import requests
import blockcypher
from django.core import signing
from django.core.signing import BadSignature, SignatureExpired
from django.contrib.contenttypes.models import ContentType
from datetime import timedelta
from django.utils import timezone
from easy_cache import ecached
from django.urls import reverse


env = environ.Env()
logger = logging.getLogger(__name__)
CONFIRMATIONS = env('CONFIRMATIONS', default=6)


def get_api_key():
    from .models import ApiKey
    api_key = env('DEFAULT_BLOCKCYPHER_API_KEY', '')
    if api_key:
        ApiKey.objects.get_or_create(api_key=api_key)
    return ApiKey.live.first()


def get_all_api_keys():
    from .models import ApiKey
    return ApiKey.objects.all()


def to_satoshi(amount):
    if type(amount) is float:
        return int(amount * 100000000)
    elif type(amount) is str:
        try:
            amount = float(amount)
            return int(amount * 100000000)
        except:
            raise ValueError('Can not convert string to float')
    else:
        raise ValueError('Amount must be float')


def from_satoshi(amount):
    if type(amount) is int:
        return float(amount / 100000000)
    elif type(amount) is str:
        try:
            amount = float(amount)
            return int(amount / 100000000)
        except:
            raise ValueError('Can not convert string to float')
    else:
        raise ValueError('Amount must be integer')


def set_webhook(from_address, to_address, transaction_id,
                coin_symbol, event='tx-confirmation'):

    domain = env('DOMAIN_NAME')

    signature = signing.dumps({
        'from_address': from_address,
        'to_addresses': to_address,
        'symbol': coin_symbol,
        'event': event,
        'transaction_id': transaction_id,
        })

    callback_url = 'https://{}{}'.format(
        domain,
        reverse(
            'wallets:webhook', kwargs={'signature': signature}
            )
        )

    webhook = blockcypher.subscribe_to_address_webhook(
        callback_url=callback_url,
        subscription_address=from_address,
        event=event,
        coin_symbol=coin_symbol,
        api_key=get_api_key()
    )
    return webhook


def decode_signin(signature, max_age=60*60*24*30):
    sign = None
    try:
        sign = signing.loads(signature, max_age=max_age)
    except SignatureExpired:
        logger.exception("Signature expired")
        raise SignatureExpired
    except BadSignature:
        logger.exception("Signature invalid")
        raise BadSignature
    return sign


def validate_signin(data):
    key_list = ['from_address', 'to_addresses', 'symbol', 'event',
                'transaction_id', 'invoice_id', 'content_type']
    symbol_list = ['bcy', 'btc', 'ltc', 'dash', 'doge']
    event_list = ['tx-confidence', 'double-spend-tx', 'tx-confirmation',
                  'confirmed-tx', 'new-block', 'unconfirmed-tx']

    if all(key in data for key in key_list):
        assert data['symbol'] in symbol_list, '{}'.format(data['symbol'])
        assert data['event'] in event_list, '{}'.format(len(data['event']))


def extract_webhook_id(signature, coin_symbol):
    api_keys = get_all_api_keys()
    for api_key in api_keys:
        webhook_id = None
        can_unsubscribe = False
        webhooks = blockcypher.list_webhooks(api_key, coin_symbol=coin_symbol)
        for webhook in webhooks:
            if webhook['url'].endswith(signature + '/'):
                webhook_id = webhook['id']
                webhook_confirmations = webhook.get('confirmations', None)
                if webhook_confirmations:
                    if webhook['confirmations'] >= CONFIRMATIONS:
                        can_unsubscribe = True
                return {
                    'api_key': api_key,
                    'webhook_id': webhook_id,
                    'can_unsubscribe': can_unsubscribe
                }


def unsubscribe_from_webhook(api_key, webhook_id,
                             can_unsubscribe, coin_symbol):
    if can_unsubscribe:
        unsubscribe = blockcypher.unsubscribe_from_webhook(
            api_key,
            webhook_id,
            coin_symbol=coin_symbol
        )
    return unsubscribe


def get_wallet_model(symbol):
    model = None
    from .models import Btc, Ltc, Doge, Dash, Bcy
    data = {
        'btc': Btc, 'ltc': Ltc, 'dash': Dash, 'doge': Doge, 'bcy': Bcy
    }
    if symbol in data:
        model = data[symbol]
    return model


class GetWebhook(object):
    """docstring for GetWebhook"""
    def __init__(self, signal):
        super(GetWebhook, self).__init__()
        self.signal = signal
        self.from_address = None
        self.to_addresses = None
        self.symbol = None
        self.event = None
        self.transaction_id = None
        self.paylaod = {}
        self.sender_wallet = None
        self.receiver_wallets = []
        self.parse_signal()
        self.get_object()

    def parse_signal(self):
        key_list = [
            'from_address', 'to_addresses', 'symbol',
            'event', 'transaction_id'
        ]
        assert all(key in self.signal for key in key_list), (
            'The data in the received signal is not enough'
        )
        for item in key_list:
            setattr(self, item, self.signal[item])

    def get_object(self):
        symbols = ['btc', 'ltc', 'dash', 'doge', 'bcy']
        assert self.symbol in symbols, (
            'Received unsupported coin symbol ({})'.format(self.symbol)
        )

        content_type = ContentType.objects.get(
            app_label='wallets',
            model=self.symbol.lower()
        )
        try:
            sender_wallet = content_type.get_object_for_this_type(
                address=self.from_address
            )
            self.sender_wallet = sender_wallet

        except Exception as e:
            logger.exception(e)
            self.sender_wallet = None

        for address in self.to_addresses:
            try:
                receiver_wallet = content_type.get_object_for_this_type(
                    address=address
                )
                self.receiver_wallets.append(receiver_wallet)
            except Exception as e:
                logger.exception(e)


class CheckTransactionConfirmations(GetWebhook):
    """docstring for CheckTransactionConfirmations"""
    def __init__(self, signal, confirmations=CONFIRMATIONS):
        super(CheckTransactionConfirmations, self).__init__(signal)
        self.confirmations = confirmations
        self.confirmed = False
        self.transaction = None
        self.processing()

    def find_transaction(self):
        if self.sender_wallet:
            for transaction in self.sender_wallet.transactions:
                if self.transaction_id in transaction['tx_hash']:
                    self.transaction = transaction

    def check_confirmations(self):
        if self.transaction:
            if self.transaction['confirmations'] >= self.confirmations:
                self.confirmed = True

    def processing(self):
        self.find_transaction()
        self.check_confirmations()


class Converter(object):
    """docstring for Converter"""
    def __init__(self, currency_to, currency_from):
        super(Converter, self).__init__()
        self.currency_to = currency_to
        self.currency_from = currency_from
        self.currencies = self.get_currencies()
        self.validate()
        self.result = self.convert()

    def __repr__(self):
        return str(self.result)

    def get_currencies(self):
        return {
            'btc': 'bitcoin',
            'ltc': 'litecoin',
            'dash': 'dash',
            'doge': 'dogecoin'
        }

    def validate(self):
        assert self.currency_to != self.currency_from, (
            'It is not possible to convert {} to {}'.format(
                self.currency_to, self.currency_from
            )
        )
        assert self.currency_to in self.currencies, (
            'The converter is not provided for {}'.format(
                self.currency_to
            )
        )
        assert self.currency_from in self.currencies, (
            'The converter is not provided for {}'.format(
                self.currency_from
            )
        )

    @ecached('convert', 60)
    def convert(self):
        currency_from = self.currencies[self.currency_from]
        currency_to = self.currencies[self.currency_to]

        from_response = requests.get(
            'https://api.coinmarketcap.com/v1/ticker/{}/'.format(
                currency_from
            )
        )
        from_json_response = from_response.json()
        from_price_usd = from_json_response[0]['price_usd']

        to_response = requests.get(
            'https://api.coinmarketcap.com/v1/ticker/{}/'.format(
                currency_to
            )
        )
        to_json_response = to_response.json()
        to_price_usd = to_json_response[0]['price_usd']

        return float(to_price_usd) / float(from_price_usd)


def get_expires_date():
    return timezone.now() + timedelta(seconds=60*60)
