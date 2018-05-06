from .utils import get_wallet_model
from itertools import chain
from .models import Payment


def get_payments(user, symbol):
    wallet = get_wallet_model(symbol)
    if wallet:
        wallets = wallet.objects.filter(user=user)
        q = [w.payments.all() for w in wallets]
        return list(chain(*q))


def get_invoices(user, symbol):
    wallet = get_wallet_model(symbol)
    if wallet:
        wallets = wallet.objects.filter(user=user)
        q = [w.invoices.all() for w in wallets]
        return list(chain(*q))


def get_count_unpaid_payments(user, symbol):
    payments = get_payments(user, symbol)
    if payments:
        return len(
            [i for i in payments if not i.invoice.is_paid and not i.invoice.is_expired]
        )
    return 0


def get_count_unpaid_invoices(user, symbol):
    invoices = get_invoices(user, symbol)
    if invoices:
        return len(
            [i for i in invoices if not i.is_paid and not i.is_expired]
        )
    return 0


def get_total_user_balance(user):
    total_balance = 0
    btc = user.btc_wallets.first()
    ltc = user.ltc_wallets.first()
    dash = user.dash_wallets.first()
    doge = user.doge_wallets.first()
    bcy = user.bcy_wallets.first()

    if btc:
        total_balance += btc.total_balance

    if ltc:
        total_balance += ltc.total_balance

    if dash:
        total_balance += dash.total_balance

    if doge:
        total_balance += doge.total_balance

    if bcy:
        total_balance += bcy.total_balance
    return total_balance


def get_total_user_usd_balance(user):
    total_balance = 0
    btc = user.btc_wallets.first()
    ltc = user.ltc_wallets.first()
    dash = user.dash_wallets.first()
    doge = user.doge_wallets.first()
    bcy = user.bcy_wallets.first()

    if btc:
        total_balance += btc.total_usd_balance

    if ltc:
        total_balance += ltc.total_usd_balance

    if dash:
        total_balance += dash.total_usd_balance

    if doge:
        total_balance += doge.total_usd_balance

    if bcy:
        total_balance += bcy.total_usd_balance
    return total_balance

'''
def user_total_earned(user):
    qs = []
    for symbol in ['btc', 'ltc', 'dash', 'doge', 'bcy']:
        wallet_model = get_wallet_model(symbol)
        if wallet_model:
            wallets = wallet_model.objects.filter(user=user)
            for wallet in wallets:
                for payment in wallet.payments.filter(invoice__is_paid=True):
                    if user.has_perm('view_payment', payment):
                        qs.append(payment.amount)
    return sum(qs)
'''


def user_total_earned_usd(user):
    qs = []
    for symbol in ['btc', 'ltc', 'dash', 'doge', 'bcy']:
        wallet_model = get_wallet_model(symbol)
        if wallet_model:
            wallets = wallet_model.objects.filter(user=user)
            for wallet in wallets:
                for payment in wallet.payments.filter(invoice__is_paid=True):
                    if user.has_perm('view_payment', payment):
                        rate = payment.wallet.__class__.get_rate()
                        amount = round(payment.amount * float(rate), 2)
                        qs.append(amount)
    return round(sum(qs), 2)
