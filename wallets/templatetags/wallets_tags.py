from django import template
from ..utils import get_wallet_model
register = template.Library()


@register.simple_tag(takes_context=True)
def unpaid_user_sended_invoices(context):
    request = context['request']
    if request:
        invoices_count = 0
        symbols = ['btc', 'ltc', 'dash', 'doge', 'bcy']
        for symbol in symbols:
            wallet = get_wallet_model(symbol)
            invoices_count += wallet.get_unpaid_sended_invoices(
                user=request.user,
                symbol=symbol
            )
        return invoices_count


@register.simple_tag(takes_context=True)
def unpaid_user_received_invoices(context):
    request = context['request']
    if request:
        invoices_count = 0
        symbols = ['btc', 'ltc', 'dash', 'doge', 'bcy']
        for symbol in symbols:
            wallet = get_wallet_model(symbol)
            invoices_count += wallet.get_unpaid_received_invoices(
                user=request.user,
                symbol=symbol
            )
        return invoices_count


@register.simple_tag(takes_context=True)
def unpaid_user_invoices(context):
    request = context['request']
    if request:
        invoices_count = 0
        symbols = ['btc', 'ltc', 'dash', 'doge', 'bcy']
        for symbol in symbols:
            wallet = get_wallet_model(symbol)
            invoices_count += wallet.get_unpaid_received_invoices(
                user=request.user,
                symbol=symbol
            )
            invoices_count += wallet.get_unpaid_sended_invoices(
                user=request.user,
                symbol=symbol
            )
        return invoices_count


@register.simple_tag(takes_context=True)
def unpaid_symbol_user_sended_invoices(context, symbol):
    request = context['request']
    if request:
        invoices_count = 0
        wallet = get_wallet_model(symbol)
        if wallet:
            invoices_count += wallet.get_unpaid_sended_invoices(
                user=request.user,
                symbol=symbol
            )
            return invoices_count


@register.simple_tag(takes_context=True)
def unpaid_symbol_user_received_invoices(context, symbol):
    request = context['request']
    if request:
        invoices_count = 0
        wallet = get_wallet_model(symbol)
        if wallet:
            invoices_count += wallet.get_unpaid_received_invoices(
                user=request.user,
                symbol=symbol
            )
            return invoices_count


@register.simple_tag(takes_context=True)
def unpaid_symbol_user_invoices(context):
    request = context['request']
    if request:
        invoices_count = 0
        symbols = ['btc', 'ltc', 'dash', 'doge', 'bcy']
        for symbol in symbols:
            wallet = get_wallet_model(symbol)
            invoices_count += wallet.get_unpaid_received_invoices(
                user=request.user,
                symbol=symbol
            )
            invoices_count += wallet.get_unpaid_sended_invoices(
                user=request.user,
                symbol=symbol
            )
        return invoices_count
