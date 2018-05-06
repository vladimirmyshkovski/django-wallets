from django import template
from ..queries import (get_user_total_earned_usd, get_user_total_balance_usd,
                       get_user_wallet_balance, get_user_wallet_balance_usd)


register = template.Library()

'''
@register.simple_tag(takes_context=True)
def count_unpaid_invoices(context):
    request = context.get('request', None)
    if request:
        count = 0
        symbols = ['btc', 'ltc', 'dash', 'doge', 'bcy']
        for symbol in symbols:
            count += get_count_unpaid_invoices(
                user=request.user,
                symbol=symbol
            )
        return count


@register.simple_tag(takes_context=True)
def count_unpaid_payments(context):
    request = context.get('request', None)
    if request:
        count = 0
        symbols = ['btc', 'ltc', 'dash', 'doge', 'bcy']
        for symbol in symbols:
            count += get_count_unpaid_payments(
                user=request.user,
                symbol=symbol
            )
        return count


@register.simple_tag(takes_context=True)
def count_unpaid(context):
    request = context.get('request', None)
    if request:
        count = 0
        symbols = ['btc', 'ltc', 'dash', 'doge', 'bcy']
        for symbol in symbols:
            count += get_count_unpaid_invoices(
                user=request.user,
                symbol=symbol
            )
            count += get_count_unpaid_payments(
                user=request.user,
                symbol=symbol
            )
        return count


@register.simple_tag(takes_context=True)
def count_unpaid_symbol_invoices(context, symbol):
    request = context.get('request', None)
    if request:
        return get_count_unpaid_invoices(user=request.user,
                                         symbol=symbol)


@register.simple_tag(takes_context=True)
def count_unpaid_symbol_payments(context, symbol):
    request = context.get('request', None)
    if request:
        return get_count_unpaid_payments(user=request.user,
                                         symbol=symbol)


@register.simple_tag(takes_context=True)
def count_unpaid_symbol(context, symbol):
    request = context.get('request', None)
    if request:
        count = 0
        count += get_count_unpaid_invoices(
            user=request.user,
            symbol=symbol
        )
        count += get_count_unpaid_payments(
            user=request.user,
            symbol=symbol
        )
        return count
'''
'''
@register.simple_tag(takes_context=True)
def total_earned(context):
    request = context['request']
    if request:
        user = request.user
        return user_total_earned(user)
'''


@register.simple_tag(takes_context=True)
def total_user_earned_usd(context):
    request = context.get('request', None)
    if request:
        user = request.user
        return get_user_total_earned_usd(user)


@register.simple_tag(takes_context=True)
def total_user_balance_usd(context):
    request = context.get('request', None)
    if request:
        user = request.user
        return get_user_total_balance_usd(user)


@register.simple_tag(takes_context=True)
def wallet_user_balance(context, wallet):
    request = context.get('request', None)
    if request:
        user = request.user
        return get_user_wallet_balance(user, wallet)


@register.simple_tag(takes_context=True)
def wallet_user_balance_usd(context, wallet):
    request = context.get('request', None)
    if request:
        user = request.user
        return get_user_wallet_balance_usd(user, wallet)
