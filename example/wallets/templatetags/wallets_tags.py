from django import template
from ..models import Invoice, Btc, Ltc, Dash, Doge, Bccy
from ..utils import get_wallet_model
from queryset_sequence import QuerySetSequence
register = template.Library()


@register.simple_tag(takes_context=True)
def unpaid_user_sended_invoices(context):
    request = context['request']
    if request:
        invoices_count = Invoice.objects.filter(
            sender_wallet_object__user=request.user, is_paid=False).count()
        return invoices_count


@register.simple_tag(takes_context=True)
def unpaid_user_received_invoices(context):
    request = context['request']
    if request:
        QuerySetSequence(
            Btc.objects.filter(user=request.user),
            Ltc.objects.filter(user=request.user),
            Dash.objects.filter(user=request.user),
            Doge.objects.filter(user=request.user),
            Bcy.objects.filter(user=request.user),
        )
        #invoices_count = 0
        #for symbol in ['btc', 'ltc', 'dash', 'doge', 'bcy']:
        #    model = get_wallet_model(symbol)
        #    user_models = model.objects.filter(user=request.user)
        #    for obj in user_models:
        #        invoices_count += obj.invoice_set.filter(is_paid=False).count()
        return invoices_count
