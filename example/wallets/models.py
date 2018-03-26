import requests
import blockcypher
#import environ
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.core import signing
from model_utils import Choices, FieldTracker
from django.utils.functional import cached_property
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel, SoftDeletableModel
from model_utils.fields import StatusField, MonitorField
from .utils import to_satoshi, from_satoshi

#env = environ.Env()
#domain = env('DOMAIN_NAME', default='stagingserver.xyz')
#api_key = env('BLOCKCYPHER_API_KEY')
domain = settings.DOMAIN_NAME
api_key = settings.BLOCKCYPHER_API_KEY
#domain = settings.DOMAIN_NAME
#api_key = settings.BLOCKCYPHER_API_KEY

@python_2_unicode_compatible
class BaseWallet(TimeStampedModel, SoftDeletableModel):

    private = models.CharField(max_length=150)
    public = models.CharField(max_length=150)
    address = models.CharField(max_length=150)
    wif = models.CharField(max_length=150)

    class Meta:
        abstract = True

    def __str__(self):
        return '({}) {}'.format(
            self.coin_symbol.upper(), 
            self.address
            )

    def get_absolute_url(self):
        return reverse('wallets:detail', kwargs={'wallet': self.coin_symbol, 'address': self.address})

    def save(self, *args, **kwargs):
        if not self.address:
            r = blockcypher.generate_new_address(coin_symbol=self.coin_symbol, api_key=api_key)
            self.private = r['private']
            self.public = r['public']
            self.address = r['address']
            self.wif = r['wif']
        return super(BaseWallet, self).save(*args, **kwargs)        

    def spend(self, address, amount):
        new_transaction = blockcypher.simple_spend(
            from_privkey=self.private,
            to_address=address,
            to_satoshis=to_satoshi(amount), 
            coin_symbol=self.coin_symbol,
            api_key=api_key
        )
        self.set_webhook(to_address=address, transaction=new_transaction, event='confirmed-tx')
        return new_transaction

    def set_webhook(self, to_address, transaction, event='confirmed-tx'):
        signature = signing.dumps({
            'from_address': self.address,
            'to_address': to_address,
            'symbol': self.coin_symbol,
            'event': event,
            'transaction_id': transaction
            })
        webhook = blockcypher.subscribe_to_address_webhook(
            callback_url='https://{}/wallets/webhook/{}/'.format(domain, signature),
            subscription_address=self.address,
            event=event,
            coin_symbol=self.coin_symbol,
            api_key=api_key
        )
        return webhook

    @property
    def rate(self):
        response = requests.get('https://api.coinmarketcap.com/v1/ticker/{}/'.format(self.coin_name))
        json_response = response.json()
        return json_response[0]['price_usd']

    @cached_property
    def address_details(self):
        return blockcypher.get_address_details(self.address)

    @cached_property
    def overview(self):
        return blockcypher.get_address_overview(self.address, coin_symbol=self.coin_symbol)

    @cached_property
    def balance(self):
        overview = blockcypher.get_address_overview(self.address, coin_symbol=self.coin_symbol)
        return from_satoshi(overview['balance'])

    @cached_property
    def transactions(self):
        get_address_full = blockcypher.get_address_details(self.address, coin_symbol=self.coin_symbol)
        return get_address_full['txrefs']

    @staticmethod
    def get_transaction(tx_ref, coin_symbol='btc'):
        return blockcypher.get_transaction_details(tx_ref, coin_symbol)


@python_2_unicode_compatible
class Btc(BaseWallet):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="btc_wallets", on_delete=models.CASCADE)
    coin_symbol = models.CharField(max_length=5, default='btc')
    coin_name = models.CharField(max_length=10, default='bitcoin')

    @cached_property
    def total_balance(self):
        balance = 0
        '''
        for address in self.user.btc_wallets.all():
            balance += address.balance
        '''
        return balance


@python_2_unicode_compatible
class Doge(BaseWallet):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="doge_wallets", on_delete=models.CASCADE)
    coin_symbol = models.CharField(max_length=5, default='doge')
    coin_name = models.CharField(max_length=10, default='dogecoin')

    @cached_property
    def total_balance(self):
        balance = 0
        '''
        for address in self.user.doge_wallets.all():
            balance += address.balance
        '''
        return balance


@python_2_unicode_compatible
class Ltc(BaseWallet):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="ltc_wallets", on_delete=models.CASCADE)
    coin_symbol = models.CharField(max_length=5, default='ltc')
    coin_name = models.CharField(max_length=10, default='litecoin')

    @cached_property
    def total_balance(self):
        balance = 0
        '''
        for address in self.user.ltc_wallets.all():
            balance += address.balance
        '''
        return balance


@python_2_unicode_compatible
class Dash(BaseWallet):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="dash_wallets", on_delete=models.CASCADE)
    coin_symbol = models.CharField(max_length=5, default='dash')
    coin_name = models.CharField(max_length=10, default='dash')

    @cached_property
    def total_balance(self):
        balance = 0
        '''
        for address in self.user.dash_wallets.all():
            balance += address.balance
        '''
        return balance    