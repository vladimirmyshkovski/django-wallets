#import environ
import logging
import requests
import blockcypher
from django.core import signing
from django.core.signing import BadSignature, SignatureExpired

from django.conf import settings

from django.contrib.contenttypes.models import ContentType

from functools import lru_cache

domain = settings.DOMAIN_NAME
api_key = settings.BLOCKCYPHER_API_KEY
#env = environ.Env()
logger = logging.getLogger(__name__)
#domain = env('DOMAIN_NAME')
#api_key = env('BLOCKCYPHER_API_KEY')


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


def set_webhook(from_address, to_address, transaction_id, coin_symbol,
                payload=None, event='confirmed-tx'):
    if payload:
        payload = signing.dumps(payload)

    signature = signing.dumps({
        'from_address': from_address,
        'to_addresses': to_address,
        'symbol': coin_symbol,
        'event': event,
        'transaction_id': transaction_id,
        'payload': payload
        })
    webhook = blockcypher.subscribe_to_address_webhook(
        callback_url='https://{}/wallets/webhook/{}/'.format(
            domain,
            signature
        ),
        subscription_address=from_address,
        event=event,
        coin_symbol=coin_symbol,
        api_key=api_key
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
                'transaction_id']
    symbol_list = ['bcy', 'btc', 'ltc', 'dash', 'doge']
    event_list = ['tx-confidence', 'double-spend-tx', 'tx-confirmation',
                  'confirmed-tx', 'new-block', 'unconfirmed-tx']

    if all(key in data for key in key_list):
        assert data['symbol'] in symbol_list, '{}'.format(data['symbol'])
        assert data['event'] in event_list, '{}'.format(len(data['event']))


def extract_webhook_id(signature, coin_symbol):
    webhook_id = None
    webhooks = blockcypher.list_webhooks(api_key, coin_symbol=coin_symbol)
    for webhook in webhooks:
        if webhook['url'].endswith(signature + '/'):
            webhook_id = webhook['id']
            return (webhook_id)
    return webhook_id


def unsubscribe_from_webhook(webhook_id, coin_symbol):
    unsubscribe = blockcypher.unsubscribe_from_webhook(
        api_key,
        webhook_id,
        coin_symbol=coin_symbol
    )
    return unsubscribe


def get_wallet_model(symbol):
    from .models import Btc, Ltc, Doge, Dash, Bcy

    if symbol == 'btc':
        model = Btc
    elif symbol == 'ltc':
        model = Ltc
    elif symbol == 'dash':
        model = Dash
    elif symbol == 'doge':
        model = Doge
    elif symbol == 'bcy':
        model = Bcy
    else:
        model = None
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
        if 'from_address' in self.signal:
            self.from_address = self.signal['from_address']
        if 'to_addresses' in self.signal:
            self.to_addresses = self.signal['to_addresses']
        if 'symbol' in self.signal:
            self.symbol = self.signal['symbol']
        if 'event' in self.signal:
            self.event = self.signal['event']
        if 'transaction_id' in self.signal:
            self.transaction_id = self.signal['transaction_id']
        if 'paylaod' in self.signal:
            self.paylaod = self.signal['paylaod']

    def get_object(self):
        if self.symbol:
            wallet_content_type = ContentType.objects.get(
                app_label='wallets',
                model=self.symbol.lower()
            )
            sender_wallet = wallet_content_type.get_object_for_this_type(
                address=self.from_address
            )
            self.sender_wallet = sender_wallet

            for address in self.to_addresses:
                receiver_wallet = wallet_content_type.get_object_for_this_type(
                    address=address
                )
                self.receiver_wallets.append(receiver_wallet)


class CheckTransactionConfirmations(GetWebhook):
    """docstring for CheckTransactionConfirmations"""
    def __init__(self, signal, confirmations=6):
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
        assert self.currency_to != self.currency_from, '''
        It is not possible to convert {} to {}'''.format(self.currency_to,
                                                         self.currency_from)
        assert self.currency_to in self.currencies, '''
        The converter is not provided for {}'''.format(self.currency_to)
        assert self.currency_from in self.currencies, '''
        The converter is not provided for {}'''.format(self.currency_from)

    @lru_cache(maxsize=2)
    def convert(self):
        currency_from = self.currencies[self.currency_from]
        currency_to = self.currencies[self.currency_to]

        from_response = requests.get(
            'https://api.coinmarketcap.com/v1/ticker/{}/'.format(
                currency_from)
            )
        from_json_response = from_response.json()
        from_price_usd = from_json_response[0]['price_usd']

        to_response = requests.get(
            'https://api.coinmarketcap.com/v1/ticker/{}/'.format(currency_to))
        to_json_response = to_response.json()
        to_price_usd = to_json_response[0]['price_usd']

        return float(to_price_usd) / float(from_price_usd)
