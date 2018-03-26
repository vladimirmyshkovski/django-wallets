from django.core import signing
from django.conf import settings

from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _

from django.http.response import HttpResponse
from django.http import HttpResponseBadRequest, JsonResponse, Http404

from django.urls import reverse

from django.contrib import messages

from django.db.models import Q

from django.shortcuts import redirect

from django.views.generic import DetailView, ListView, RedirectView, UpdateView, CreateView, View
from django.views.decorators.csrf import csrf_exempt

from .utils import decode_signin, extract_webhook_id, unsubscribe_from_webhook, parse_requset, parse_errors
from .signals import get_webhook
from .mixins import OwnerPermissions, CheckWallet
from .models import Btc, Ltc, Doge, Dash

from .forms import WithdrawForm

from .validators import withdraw_schema
from cerberus import Validator

v = Validator()
#from dal import autocomplete


class BaseWalletView(CheckWallet, OwnerPermissions):
    pass


class WalletsCreateView(BaseWalletView, RedirectView):

    def post(self, request, *args, **kwargs):
        
        wallet = self.check_wallet(self.kwargs['wallet'])

        try:
            address = wallet.objects.create(user=request.user)
            self.address = address 
            messages.add_message(self.request, messages.SUCCESS, _('New {} address successfully created'.format(address.coin_symbol.upper())))
        except:
            messages.add_message(self.request, messages.ERROR, _('Something wrong, try again later'))
        return super(WalletsCreateView, self).post(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        if self.address:
            return self.address.get_absolute_url


class WalletsListView(CheckWallet, OwnerPermissions, ListView):

    template_name = 'wallets/list.html'
    context_object_name = 'list'
    
    def get_queryset(self, queryset=None):
        
        if self.wallet:
            queryset = wallet.objects.filter(user=self.request.user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(WalletsListView, self).get_context_data(**kwargs)
        balance = 0
        if self.get_queryset():
            for address in self.get_queryset():
                balance += address.balance
        
        context['total_balance'] = balance
        context['symbol'] = self.wallet #self.kwargs['wallet']
        return context

    def dispatch(self, request, *args, **kwargs):
        self.wallet = self.check_wallet(self.kwargs['wallet'])
        if not self.wallet:
            raise Http404('Wallet does not exist')
        return super(WalletsListView, self).dispatch(request, *args, **kwargs)


class WalletsDetailView(BaseWalletView, DetailView):

    slug_field = 'address'
    slug_url_kwarg = 'address'
    template_name = 'wallets/detail.html'

    def get_object(self, queryset=None):
        model = self.check_wallet(self.kwargs['wallet'])
        if model:
            return model.objects.filter(address=self.kwargs['address']).first()
        raise Http404('Wallet does not exist')

    def get_context_data(self, **kwargs):
        context = super(WalletsDetailView, self).get_context_data(**kwargs)
        context['form'] = WithdrawForm
        return context

class WalletsWithdrawView(BaseWalletView, RedirectView):

    http_method_names = [u'post', u'get']

    def get_object(self, queryset=None):
        model = self.check_wallet(self.kwargs['wallet'])
        if model:
            return model.objects.filter(address=self.kwargs['address']).first()

    def post(self, request, *args, **kwargs):
        
        data = parse_requset(request)
        #v.va = validate_requset(data, withdraw_schema)
        print(v.validate(data, withdraw_schema))
        if not v.validate(data, withdraw_schema) and data:
            errors = parse_errors(v.errors)
            messages.add_message(self.request, messages.ERROR, _(errors))
            return super(WalletsWithdrawView, self).post(request, *args, **kwargs)
        
        address = self.request.POST.get('address', None)
        if not address:
            messages.add_message(self.request, messages.ERROR, _('Address field can not be blank'))
            return super(WalletsWithdrawView, self).post(request, *args, **kwargs)

        amount = self.request.POST.get('amount', None)
        if not amount:
            messages.add_message(self.request, messages.ERROR, _('Amount field can not be blank'))
            return super(WalletsWithdrawView, self).post(request, *args, **kwargs)

        obj = self.get_object()

        if float(amount) > obj.balance:
            messages.add_message(self.request, messages.ERROR, _('Amount can not be more than the balance of this address.'))
            return super(WalletsWithdrawView, self).post(request, *args, **kwargs)

        try:
            transaction = obj.spend(address, float(amount))
            messages.add_message(self.request, messages.SUCCESS, _('Transaction successfully created {}'.format(transaction)))
        except:
            messages.add_message(self.request, messages.ERROR, _('Something wrong, try again later'))
        return super(WalletsWithdrawView, self).post(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        if 'wallet' in self.kwargs and 'address' in self.kwargs:
            return redirect(reverse('wallets:detail', kwargs={
                'wallet': self.kwargs['wallet'],
                'address': self.kwargs['address']
                }))
        else:
            return redirect(reverse(settings.LOGIN_URL))
    
'''



from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

class WalletsAutocompleteView(View):

    http_method_names = ['get'] 

    def get(self, request, *args, **kwargs):
        self.q = request.GET.get('q', None)
        
        if not request.user.is_authenticated:
            return []

        btc = Btc.objects.filter(user=self.request.user)
        ltc = Ltc.objects.filter(user=self.request.user)
        doge = Doge.objects.filter(user=self.request.user)
        dash = Dash.objects.filter(user=self.request.user)

        if self.q:
            btc = btc.filter(address__icontains=self.q)
            ltc = ltc.filter(address__icontains=self.q)
            doge = doge.filter(address__icontains=self.q)
            dash = dash.filter(address__icontains=self.q)

        # Aggregate querysets
        #qs = autocomplete.QuerySetSequence(btc, ltc, doge, dash)
        qs_list = []
        qs_list.append(btc)
        qs_list.append(ltc)
        qs_list.append(doge)
        qs_list.append(dash)
        for item in qs_list:
            qs = set(item)

        if self.q:
            # This would apply the filter on all the querysets
            qs = qs.filter(Q(coin_name__icontains=self.q) | Q(coin_symbol__icontains=self.q))

        # This will limit each queryset so that they show an equal number
        # of results.
        #qs = self.mixup_querysets(qs)
        
        qs = []
        return qs

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CommandReceiveView, self).dispatch(request, *args, **kwargs)        
'''

class WalletsWebhookView(View):

    http_method_names = [u'post'] 

    def post(self, request, *args, **kwargs):
        signature = kwargs['signature']
        if signature:
            sign = decode_signin(signature)
            if sign:
                get_webhook.send(
                    sender=None,
                    from_address = sign['from_address'],
                    to_address = sign['to_address'],
                    symbol = sign['symbol'],
                    event = sign['event'],
                    transaction_id = sign['transaction_id']
                    )
                webhook_id = extract_webhook_id(signature, sign['symbol'])
                if webhook_id:
                    unsubscribe = unsubscribe_from_webhook(webhook_id)
                    print(unsubscribe)
        return JsonResponse({}, status=200)

    def get(self, request, *args, **kwargs):
        return redirect(reverse(settings.LOGIN_URL))

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(WalletsWebhookView, self).dispatch(request, *args, **kwargs)