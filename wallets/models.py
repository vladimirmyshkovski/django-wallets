import logging
from typing import List

import requests
import blockcypher

from model_utils.models import TimeStampedModel, SoftDeletableModel
from guardian.shortcuts import assign_perm
from easy_cache import ecached_property

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
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.utils.html import format_html

from .managers import ApiKeyManager
from .utils import get_expires_date, from_satoshi, get_api_key
from . import api

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class ApiKey(TimeStampedModel, SoftDeletableModel):
    api_key = models.CharField(
        max_length=50,
        null=False,
        blank=True,
        unique=True
    )

    live = ApiKeyManager()

    @ecached_property('is_expire:{self.id}', 60)
    def is_expire(self):
        try:
            info = blockcypher.get_token_info(self.api_key)
            limits = info.get('limits', None)
            hits_history = info.get('hits_history', None)
            if not limits:
                return True
            if not hits_history:
                return False
            else:
                current_api_hour = sum([
                    i['api/hour'] for i in hits_history if 'api/hour' in i
                ])
                current_hooks_hour = sum([
                    i['hooks/hour'] for i in hits_history if 'hooks/hour' in i
                ])
                if current_api_hour < limits['api/hour'] and \
                   current_hooks_hour < limits['hooks/hour']:
                    return False
        except:
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
        ordering = ['id']

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

    def spend(self, addresses: List[str], amounts: List[int]) -> str:
        assert len(addresses) == len(amounts), (
            'The number of addresses and amounts should be the same'
        )
        new_transaction = api.not_simple_spend(
            from_privkey=self.private,
            to_addresses=addresses,
            to_satoshis=amounts,
            coin_symbol=self.coin_symbol,
            api_key=get_api_key()
        )
        return new_transaction

    def spend_with_webhook(self, addresses: List[str], amounts: List[int],
                           invoice: object=None, obj: object=None,
                           event: str='tx-confirmation') -> str:
        assert len(addresses) == len(amounts), (
            'The number of addresses and amounts should be the same'
        )

        new_transaction = api.not_simple_spend(
            from_privkey=self.private,
            to_addresses=addresses,
            to_satoshis=amounts,
            coin_symbol=self.coin_symbol,
            api_key=get_api_key()
        )
        self.set_webhook(
            to_addresses=addresses,
            transaction=new_transaction,
            obj=obj,
            invoice=invoice,
            event=event
        )
        return new_transaction

    def set_webhook(self, to_addresses: List[str], transaction: str,
                    obj: object=None, invoice: object=None,
                    event: str='tx-confirmation') -> str:
        domain = settings.DOMAIN_NAME
        if obj:
            try:
                obj = signing.dumps({
                    'app_label': obj._meta.app_label,
                    'model': obj._meta.model_name,
                    'id': obj.id
                })
            except Exception:
                obj = None

        signature = signing.dumps({
            'from_address': self.address,
            'to_addresses': to_addresses,
            'symbol': self.coin_symbol,
            'event': event,
            'transaction_id': transaction,
            'invoice_id': invoice.id if invoice else None,
            'content_object': obj
        })
        callback_url = 'https://{}/wallets/webhook/{}/'.format(
            domain, signature
        )
        webhook = blockcypher.subscribe_to_address_webhook(
            callback_url=callback_url,
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

    @ecached_property('natural_balance:{self.id}', 60)
    def normal_balance(self):
        return from_satoshi(self.balance)

    @ecached_property('usd_balance:{self.id}', 60)
    def usd_balance(self):
        return round((self.normal_balance * self.__class__.get_rate()), 2)

    @ecached_property('transactions:{self.id}', 60)
    def transactions(self):
        get_address_full = self.address_details
        return get_address_full['txrefs']

    @staticmethod
    def transaction_details(tx_ref: str, coin_symbol='btc') -> dict:
        details = blockcypher.get_transaction_details(tx_ref, coin_symbol)
        return details

    def create_invoice(self, content_object: object, data: list) -> object:
        key_list = ['wallet', 'amount', 'content_object', 'purpose']

        invoice = Invoice.objects.create(
            wallet=self,
            content_object=content_object
        )
        assign_perm('pay_invoice', self.user, invoice)
        assign_perm('view_invoice', self.user, invoice)

        for item in data:
            if all(key in item for key in key_list):
                payment = Payment(
                    invoice=invoice,
                    amount=item['amount'],
                    wallet=item['wallet'],
                    content_object=item['content_object'],
                    purpose=item['purpose']
                )
                payment.save()
                assign_perm('view_payment', self.user, payment)
                assign_perm('view_payment', item['wallet'].user, payment)
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
        try:
            response = requests.get(
                'https://api.coinmarketcap.com/v1/ticker/{}/'.format(
                    coin_name
                )
            )
            json_response = response.json()
            return round(float(json_response[0]['price_usd']), 2)
        except Exception:
            return 0


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

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    tx_ref = models.CharField(max_length=100, null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    expires = models.DateTimeField(default=get_expires_date)

    class Meta:
        ordering = ['id']
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

    @property
    def normal_amount(self):
        return format(from_satoshi(self.amount), '.8f')

    @property
    def usd_amount(self):
        return round((self.normal_amount * self.wallet.get_rate()), 2)

    def pay(self):
        if self.wallet.user.has_perm('pay_invoice', self) \
           and not self.is_expired:
            payments = self.payments.all()
            data = [
                {
                    'address': payment.wallet.address,
                    'amount':  payment.amount
                } for payment in payments
            ]
            tx_ref = self.wallet.spend(
                addresses=[payment['address'] for payment in data],
                amounts=[payment['amount'] for payment in data],
                invoice=self,
                obj=self.content_object
            )
            self.tx_ref = tx_ref
            self.save()
            return tx_ref
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
        related_name='payments'
    )
    wallet_id = models.PositiveIntegerField()
    wallet = GenericForeignKey(
        'wallet_type',
        'wallet_id'
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    purpose = models.CharField(max_length=255)

    class Meta:
        ordering = ['id']
        permissions = (
            ('view_payment', _('Can view payment')),
        )

    @property
    def normal_amount(self):
        return float(format(from_satoshi(self.amount), '.8f'))

    @property
    def usd_amount(self):
        return round((self.normal_amount * self.wallet.get_rate()), 2)

    @property
    def text(self):
        return 'User {user} paid {amount} \
                {symbol} for {purpose} ({obj})'.format(
            user=self.invoice.wallet.user,
            amount=self.amount,
            symbol=self.invoice.wallet.coin_symbol.upper(),
            purpose=self.purpose,
            obj=self.content_object.__str__()
            )

    @property
    def html(self):
        try:
            html = format_html(
                'User <a href="{}">{}</a> paid {} {} for' +
                ' {} <a href="{}">({})</a>',
                self.invoice.wallet.user.get_absolute_url(),
                self.invoice.wallet.user,
                self.amount,
                self.invoice.wallet.coin_symbol.upper(),
                self.purpose,
                self.content_object.get_absolute_url(),
                self.content_object.__str__()
            )
            return html
        except:
            return ''
