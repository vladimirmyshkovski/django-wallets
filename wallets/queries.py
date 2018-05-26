from itertools import chain, groupby

from easy_cache import ecached

from datetime import timedelta
from django.utils import timezone

from .utils import get_wallet_model, from_satoshi
from .models import Payment


@ecached('get_payments_{user}_{symbol}', 300)
def get_payments(user, symbol):
    wallet = get_wallet_model(symbol)
    if wallet:
        wallets = wallet.objects.filter(user=user)
        q = [w.payments.all() for w in wallets]
        return list(chain(*q))


@ecached('get_invoices_{user}_{symbol}', 300)
def get_invoices(user, symbol):
    wallet = get_wallet_model(symbol)
    if wallet:
        wallets = wallet.objects.filter(user=user)
        q = [w.invoices.all() for w in wallets]
        return list(chain(*q))


@ecached('get_count_unpaid_payments_{user}_{symbol}', 300)
def get_count_unpaid_payments(user, symbol):
    payments = get_payments(user, symbol)
    if payments:
        return len(
            [i for i in payments if not i.invoice.is_paid and not i.invoice.is_expired]
        )
    return 0


@ecached('get_count_unpaid_invoices_{user}_{symbol}', 300)
def get_count_unpaid_invoices(user, symbol):
    invoices = get_invoices(user, symbol)
    if invoices:
        return len(
            [i for i in invoices if not i.is_paid and not i.is_expired]
        )
    return 0


@ecached('get_user_total_earned_usd_{user}', 300)
def get_user_total_earned_usd(user):
    total_earned_usd = 0
    for symbol in ['btc', 'ltc', 'dash', 'doge', 'bcy']:
        wallet_model = get_wallet_model(symbol)
        if wallet_model:
            wallets = wallet_model.objects.filter(user=user)
            for wallet in wallets:
                for payment in wallet.payments.filter(invoice__is_paid=True):
                    if user.has_perm('view_payment', payment):
                        #rate = payment.wallet.__class__.get_rate()
                        #amount = round(payment.amount * float(rate), 2)
                        total_earned_usd += payment.usd_amount
    return total_earned_usd


@ecached('get_user_total_paid_usd_{user}', 300)
def get_user_total_paid_usd(user):
    total_paid = 0
    for symbol in ['btc', 'ltc', 'dash', 'doge', 'bcy']:
        wallet_model = get_wallet_model(symbol)
        if wallet_model:
            wallets = wallet_model.objects.filter(user=user)
            for wallet in wallets:
                for invoice in wallet.invoices.filter(is_paid=True):
                    total_paid += invoice.usd_amount
    return total_paid


@ecached('get_user_wallet_balance_{user}_{symbol}', 300)
def get_user_wallet_balance(user, symbol):
    wallet_model = get_wallet_model(symbol)
    if wallet_model:
        wallets = wallet_model.objects.filter(user=user)
        return from_satoshi(sum([wallet.balance for wallet in wallets]))


@ecached('get_user_wallet_balance_usd_{user}_{symbol}', 300)
def get_user_wallet_balance_usd(user, symbol):
    wallet_model = get_wallet_model(symbol)
    rate = wallet_model.get_rate()
    balance = get_user_wallet_balance(user, symbol)
    return round((balance * rate), 3)


@ecached('get_user_total_balance_usd_{user}', 300)
def get_user_total_balance_usd(user):
    balance = 0
    for symbol in ['btc', 'ltc', 'dash', 'doge', 'bcy']:
        balance += float(get_user_wallet_balance_usd(user, symbol))
    return round(balance, 3)


@ecached('get_aggregate_invoices_{user}', 3600)
def get_aggregate_invoices(user):
    payments_ids = []
    for symbol in ['btc', 'ltc', 'dash', 'doge', 'bcy']:
        wallet = get_wallet_model(symbol)
        if wallet:
            wallets = wallet.objects.filter(user=user)
            q = list(chain(*[
                w.payments.values_list('id', flat=True) for w in wallets
            ]))
            if q:
                payments_ids.extend(q)
    payments = Payment.objects.filter(
        id__in=payments_ids,
        created__gte=timezone.now()-timedelta(days=7)
        ).only('modified', 'amount', 'invoice').order_by('modified')
    aggregate_payments = {
        k: round(sum(float(x.invoice.usd_amount) for x in g), 2)
        for k, g in groupby(
            payments, key=lambda i: i.modified.strftime('%d.%m.%Y')
        )
    }
    return aggregate_payments
