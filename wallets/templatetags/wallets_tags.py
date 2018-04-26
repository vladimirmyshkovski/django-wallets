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
        '''
        invoices_count = Invoice.objects.filter(
            sender_wallet_object__user=request.user, is_paid=False).count()
        '''
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
        '''
        for symbol in ['btc', 'ltc', 'dash', 'doge', 'bcy']:
            model = get_wallet_model(symbol)
            user_models = model.objects.filter(user=request.user)
            for obj in user_models:
                invoices_count += obj.invoice_set.filter(is_paid=False).count()
        '''
        return invoices_count
