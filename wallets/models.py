import logging
import environ
import requests
import blockcypher
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.core import signing
from django.utils.functional import cached_property
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from model_utils.models import TimeStampedModel, SoftDeletableModel
from django.core.validators import MinValueValidator
from guardian.shortcuts import assign_perm
from easy_cache import ecached_property
from django.utils import timezone
from .managers import ApiKeyManager
from .utils import get_expires_date, from_satoshi, get_api_key
from . import api

#domain = settings.DOMAIN_NAME
#api_key = settings.BLOCKCYPHER_API_KEY
env = environ.Env()
logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class ApiKey(TimeStampedModel, SoftDeletableModel):
    api_key = models.CharField(max_length=50, null=False, blank=True)

    live = ApiKeyManager()

    '''
    @property
    def token_info(self):
        return blockcypher.get_token_info(self.api_key)

    @property
    def limit_api_hour(self):
        return self.token_info['limits']['api/hour']

    @property
    def limit_hooks_hour(self):
        self.token_info['limits']['hooks/hour']
    '''
    @ecached_property('is_expire:{self.id}', 60)
    def is_expire(self):
        info = blockcypher.get_token_info(self.api_key)
        limits = info['limits']
        current_api_hour = sum([
            i['api/hour'] for i in info['hits_history']
        ])
        current_hooks_hour = sum([
            i['hooks/hour'] for i in info['hits_history'] if 'hooks/hour' in i
        ])
        if current_api_hour < limits['api/hour'] and \
           current_hooks_hour < limits['hooks/hour']:
            return False
        return True

    def __str__(self):
        return self.api_key


@python_2_unicode_compatible
class BaseWallet(TimeStampedModel, SoftDeletableModel):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='%(class)s_wallets',
        on_delete=models.CASCADE
    )

    private = models.CharField(max_length=150, unique=True)
    public = models.CharField(max_length=150, unique=True)
    address = models.CharField(max_length=150, unique=True)
    wif = models.CharField(max_length=150, unique=True)

    invoices = GenericRelation(
        'wallets.Invoice',
        content_type_field='wallet_type',
        object_id_field='wallet_id',
    )

    payments = GenericRelation(
        'wallets.Payment',
        content_type_field='wallet_type',
        object_id_field='wallet_id',
    )

    class Meta:
        abstract = True

    def __str__(self):
        return '({}) {}'.format(
            self.coin_symbol.upper(),
            self.address)

    def get_absolute_url(self):
        return reverse('wallets:detail', kwargs={
            'wallet': self.coin_symbol,
            'address': self.address
        })

    @cached_property
    def coin_symbol(self):
        coin_symbol = self.__class__.get_coin_symbol()
        return coin_symbol

    @cached_property
    def coin_name(self):
        coin_name = self.__class__.get_coin_name()
        return coin_name

    def spend(self, addresses, amounts):
        new_transaction = api.not_simple_spend(
            from_privkey=self.private,
            to_addresses=addresses,
            to_satoshis=amounts,
            coin_symbol=self.coin_symbol,
            api_key=get_api_key()  # settings.BLOCKCYPHER_API_KEY
        )
        return new_transaction

    def spend_with_webhook(self, addresses, amounts, payload=None):
        new_transaction = api.not_simple_spend(
            from_privkey=self.private,
            to_addresses=addresses,
            to_satoshis=amounts,
            coin_symbol=self.coin_symbol,
            api_key=get_api_key()  # settings.BLOCKCYPHER_API_KEY
        )
        self.set_webhook(
            to_addresses=addresses,
            transaction=new_transaction,
            event='confirmed-tx',
            payload=payload
        )
        return new_transaction

    def set_webhook(self, to_addresses, transaction,
                    payload=None, event='confirmed-tx'):

        domain = env('DOMAIN_NAME')

        if payload:
            payload = signing.dumps(payload)
        signature = signing.dumps({
            'from_address': self.address,
            'to_addresses': to_addresses,
            'symbol': self.coin_symbol,
            'event': event,
            'transaction_id': transaction,
            'payload': payload
        })
        webhook = blockcypher.subscribe_to_address_webhook(
            callback_url='https://{}/wallets/webhook/{}/'.format(
                domain, signature
            ),
            subscription_address=self.address,
            event=event,
            coin_symbol=self.coin_symbol,
            api_key=get_api_key()  # settings.BLOCKCYPHER_API_KEY
        )
        return webhook

    @ecached_property('address_details:{self.id}', 60)
    def address_details(self):
        details = blockcypher.get_address_details(
            self.address,
            coin_symbol=self.coin_symbol
        )
        return details

    @ecached_property('overview:{self.id}', 60)
    def overview(self):
        overview = blockcypher.get_address_overview(
            self.address,
            coin_symbol=self.coin_symbol
        )
        return overview

    @ecached_property('balance:{self.id}', 60)
    def balance(self):
        overview = blockcypher.get_address_overview(
            self.address,
            coin_symbol=self.coin_symbol
        )
        return overview['balance']

    @ecached_property('transactions:{self.id}', 60)
    def transactions(self):
        get_address_full = self.address_details
        return get_address_full['txrefs']

    @staticmethod
    def transaction_details(tx_ref, coin_symbol='btc'):
        details = blockcypher.get_transaction_details(tx_ref, coin_symbol)
        return details

    def create_invoice(self, wallets, amounts):
        assert len(wallets) == len(amounts), (
            'The number of amounts must be equal to the number of wallets')

        invoice = Invoice.objects.create(
            wallet=self
        )

        assign_perm('pay_invoice', self.user, invoice)
        assign_perm('view_invoice', self.user, invoice)

        data = dict(zip(wallets, amounts))
        for item in data:
            payment = Payment.objects.create(
                invoice=invoice,
                wallet=item,
                amount=data[item]
            )
            assign_perm('view_payment', item.user, payment)
            assign_perm('view_payment', self.user, payment)
        '''
        i = 0
        for _ in range(len(wallets)):
            Payment.objects.create(
                invoice=invoice,
                amount=amounts[i],
                receiver_wallet_object=wallets[i]
                )
            i += 1
        '''

        #for wallet in invoice.receiver_wallet_object.all():
        #    assign_perm('view_invoice', wallet.user, invoice)

        return invoice

    @classmethod
    def _get_coin_symbol_and_name(cls):
        if cls.__name__.lower().startswith('btc'):
            coin_symbol = 'btc'
            coin_name = 'bitcoin'
        elif cls.__name__.lower().startswith('ltc'):
            coin_symbol = 'ltc'
            coin_name = 'litecoin'
        elif cls.__name__.lower().startswith('dash'):
            coin_symbol = 'dash'
            coin_name = 'dash'
        elif cls.__name__.lower().startswith('doge'):
            coin_symbol = 'doge'
            coin_name = 'dogecoin'
        elif cls.__name__.lower().startswith('bcy'):
            coin_symbol = 'bcy'
            coin_name = 'blockcypher'
        return {'coin_symbol': coin_symbol, 'coin_name': coin_name}

    @classmethod
    def get_coin_symbol(cls):
        return cls._get_coin_symbol_and_name()['coin_symbol']

    @classmethod
    def get_coin_name(cls):
        return cls._get_coin_symbol_and_name()['coin_name']

    @classmethod
    def get_rate(cls):
        coin_name = cls.get_coin_name()
        response = requests.get(
            'https://api.coinmarketcap.com/v1/ticker/{}/'.format(coin_name))
        json_response = response.json()
        return json_response[0]['price_usd']

    @ecached_property('total_balance:{self.id}', 60)
    def total_balance(self):
        balance = 0
        related_name = getattr(
            self.user,
            '{}_wallets'.format(self.coin_symbol)
        )
        queryset = getattr(
            related_name,
            'all'
        )

        for address in queryset():
            balance += address.balance
        return balance

    @ecached_property('total_balance:{self.id}', 60)
    def total_usd_balance(self):
        balance = 0
        related_name = getattr(
            self.user,
            '{}_wallets'.format(self.coin_symbol)
        )
        queryset = getattr(
            related_name,
            'all'
        )

        for address in queryset():
            balance += address.balance
        return balance * self.get_rate()


@python_2_unicode_compatible
class Btc(BaseWallet):
    pass


@python_2_unicode_compatible
class Doge(BaseWallet):
    pass


@python_2_unicode_compatible
class Ltc(BaseWallet):
    pass


@python_2_unicode_compatible
class Dash(BaseWallet):
    pass


@python_2_unicode_compatible
class Bcy(BaseWallet):
    pass

    @property
    def rate(self):
        return 0


@python_2_unicode_compatible
class Invoice(TimeStampedModel, SoftDeletableModel):

    limit = models.Q(app_label='wallets', model='btc') | \
        models.Q(app_label='wallets', model='ltc') | \
        models.Q(app_label='wallets', model='dash') | \
        models.Q(app_label='wallets', model='doge') | \
        models.Q(app_label='wallets', model='bcy')

    wallet_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to=limit,
        related_name='invoices'
    )
    wallet_id = models.PositiveIntegerField()
    wallet = GenericForeignKey(
        'wallet_type',
        'wallet_id'
    )

    tx_ref = models.CharField(max_length=100, null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    expires = models.DateTimeField(default=get_expires_date)

    class Meta:
        permissions = (
            ('view_invoice', _('Can view invoice')),
            ('pay_invoice', _('Can pay invoice')),
        )

    def __init__(self, *args, **kwargs):
        super(Invoice, self).__init__(*args, **kwargs)
        self.__tracked_fields = ['is_paid']
        self.set_original_values()

    def save(self, *args, **kwargs):
        self.full_clean()
        if self.has_changed():
            if not self.can_be_paid():
                self.reset_original_values()
        self.set_original_values()
        return super(Invoice, self).save(*args, **kwargs)

    def set_original_values(self):
        for field in self.__tracked_fields:
            if getattr(self, field) is 'True':
                setattr(self, '__original_%s' % field, True)
            elif getattr(self, field) is 'False':
                setattr(self, '__original_%s' % field, False)
            else:
                setattr(self, '__original_%s' % field, getattr(self, field))
        return self.__dict__

    def has_changed(self):
        for field in self.__tracked_fields:
            original = '__original_%s' % field
            return getattr(self, original) != getattr(self, field)

    def reset_original_values(self):
        values = {}
        for field in self.__tracked_fields:
            original = '__original_%s' % field
            setattr(self, field, getattr(self, original))
            values[field] = getattr(self, field)
        return values

    @property
    def amount(self):
        return sum([payment.amount for payment in self.payments.all()])

    def pay(self, payload=None):
        if self.wallet.user.has_perm('pay_invoice', self):
            payments = self.payments.all()
            data = [
                {
                    'address': payment.wallet.address,
                    'amount':  payment.amount
                } for payment in payments
            ]
            tx_ref = self.wallet.spend_with_webhook(
                addresses=[payment['address'] for payment in data],
                amounts=[payment['amount'] for payment in data],
                payload=payload
            )
            self.tx_ref = tx_ref
            return tx_ref
            '''
            wallets = self.receiver_wallet_object.all()
            addresses = [wallet.address for wallet in wallets]
            amounts = [amount for amount in self.amount]
            tx_ref = self.sender_wallet_object.spend_with_webhook(
                addresses=addresses,
                amounts=amounts,
                payload=payload
            )
            invoice_transaction = InvoiceTransaction.objects.create(
                invoice=self,
                tx_ref=tx_ref
            )
            return invoice_transaction.tx_ref
            '''
        return None

    def get_absolute_url(self):
        return reverse('wallets:invoice_detail', kwargs={'pk': self.pk})

    @property
    def is_expired(self):
        return timezone.now() > self.expires

    def can_be_paid(self):
        if self.is_expired:
            return False

        details = self.wallet.transaction_details(
            self.tx_ref,
            self.wallet.coin_symbol
        )

        if self.amount < details['outputs'][0]['value']:
            logger.error(
                'Invoice can be confirmed, because the amount of all ' +
                'transactions is less than the amount of the invoice.'
            )
            return False

        return True

    @ecached_property('normal_amount:{self.id}', 60*5)
    def normal_amount(self):
        return from_satoshi(self.amount)


@python_2_unicode_compatible
class Payment(TimeStampedModel, SoftDeletableModel):

    limit = models.Q(app_label='wallets', model='btc') | \
        models.Q(app_label='wallets', model='ltc') | \
        models.Q(app_label='wallets', model='dash') | \
        models.Q(app_label='wallets', model='doge') | \
        models.Q(app_label='wallets', model='bcy')

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='payments',
        null=False,
        blank=True
    )

    amount = models.BigIntegerField(validators=[MinValueValidator(0)])

    wallet_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to=limit,
    )
    wallet_id = models.PositiveIntegerField()
    wallet = GenericForeignKey(
        'wallet_type',
        'wallet_id'
    )

    class Meta:
        permissions = (
            ('view_payment', _('Can view payment')),
        )
'''
@python_2_unicode_compatible
class InvoiceTransaction(models.Model):

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='tx_refs'
    )
    tx_ref = models.CharField(max_length=100, null=True, blank=False)

    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.tx_ref
'''
