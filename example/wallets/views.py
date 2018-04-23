from django.core import signing
from django.conf import settings
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.http import JsonResponse, Http404
from django.urls import reverse
from django.shortcuts import redirect
from django.views.generic import DetailView, ListView, RedirectView, View, TemplateView
from django.views.generic.edit import FormMixin, FormView
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from .utils import get_wallet_model, decode_signin, extract_webhook_id, unsubscribe_from_webhook, validate_signin
from .signals import get_webhook
from .mixins import OwnerPermissionsMixin, CheckWalletMixin
from .models import Btc, Ltc, Doge, Dash, Invoice
from .forms import WithdrawForm
from .serializers import WithdrawSerializer
from .services import generate_new_address, get_wallet_invoices
from django.core.signing import BadSignature, SignatureExpired


try:
    _messages = 'django.contrib.messages' in settings.INSTALLED_APPS

except AttributeError: # pragma: no cover
    _messages = False

if _messages: # pragma: no cover 
    from django.contrib import messages


class BaseWalletMixin(CheckWalletMixin, OwnerPermissionsMixin):
    pass


class AllUserWalletsList(LoginRequiredMixin, TemplateView):

    template_name = 'wallets/all.html'

    def get_context_data(self, **kwargs):
        context = super(AllUserWalletsList, self).get_context_data(**kwargs)
        context['btc_wallets'] = self.request.user.btc_wallets.all()
        context['ltc_wallets'] = self.request.user.ltc_wallets.all()
        context['dash_wallets'] = self.request.user.dash_wallets.all()
        context['doge_wallets'] = self.request.user.doge_wallets.all()
        return context


class WalletsCreateView(BaseWalletMixin, RedirectView):

    def get(self, request, *args, **kwargs):
        address = generate_new_address(
            user = request.user,
            coin_symbol = self.kwargs['wallet']
        )
        self.address = address
        if address:
            if _messages: # pragma: no cover 
                messages.add_message(
                    self.request,
                    messages.SUCCESS,
                    _('New {} address successfully created'.format(address.coin_symbol.upper()))
                )
        else:
            if _messages: # pragma: no cover 
                messages.add_message(self.request, messages.ERROR, _('Something wrong, try again later'))
        return super(WalletsCreateView, self).get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        if self.address:
            return self.address.get_absolute_url()
        else:
            return reverse('wallets:all')


class WalletsListView(BaseWalletMixin, ListView):

    template_name = 'wallets/list.html'
    context_object_name = 'wallets_list'
    
    def get_queryset(self, queryset=None):
        return self.wallet.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super(WalletsListView, self).get_context_data(**kwargs)
        balance = 0
        
        for address in self.get_queryset():
            balance += address.balance
        
        context['total_balance'] = balance
        context['symbol'] = self.wallet.get_coin_symbol()
        return context
    
    def dispatch(self, request, *args, **kwargs):
        self.wallet = self.check_wallet(self.kwargs['wallet'])
        if not self.wallet:
            raise Http404('Wallet does not exist')
        return super(WalletsListView, self).dispatch(request, *args, **kwargs)


class WalletsDetailView(BaseWalletMixin, FormMixin, DetailView):

    template_name = 'wallets/detail.html'
    form_class = WithdrawForm

    def get_object(self, queryset=None):
        model = self.check_wallet(self.kwargs['wallet'])
        if model:
            self.object = model.objects.get(address=self.kwargs['address'])
            return self.object
        raise Http404('Wallet does not exist')

    def get_context_data(self, **kwargs):
        context = super(WalletsDetailView, self).get_context_data(**kwargs)
        context['form'] = self.get_form()#self.request.POST, obj=self.object)#initial={'post': self.object})#self.request.POST)#initial={'post': self.object})
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)        

    def get_form(self):
        if self.request.POST:
            return self.form_class(
                data = self.request.POST,
                obj = self.object
            )
        else:
            return self.form_class


    def form_valid(self, form):
        transaction = form.spend()
        if _messages: # pragma: no cover 
            messages.add_message(
                self.request,
                messages.SUCCESS,
                _('Transaction successfully created {}'.format(transaction))
            )
        return super(WalletsDetailView, self).form_valid(form)        

    def get_success_url(self):
        return reverse(
            'wallets:detail',
            kwargs={
                    'wallet': self.kwargs['wallet'],
                    'address': self.kwargs['address']
                }
            )
'''
class WalletsWithdrawView(BaseWalletView, FormView):

    http_method_names = [u'post', u'get']

    def get_object(self, queryset=None):
        model = self.check_wallet(self.kwargs['wallet'])
        if model:
            return model.objects.get(address=self.kwargs['address'])

    def post(self, request, *args, **kwargs):    
        serializer = WithdrawSerializer(data = request.POST)
        if not serializer.is_valid():
            errors = serializer.errors
            if _messages:
                for error in errors:
                    messages.add_message(self.request, messages.ERROR, _(error))
            return super(WalletsWithdrawView, self).post(request, *args, **kwargs)
        
        address = self.request.POST.get('address', None)
        if not address:
            if _messages:
                messages.add_message(self.request, messages.ERROR, _('Address field can not be blank'))
            return super(WalletsWithdrawView, self).post(request, *args, **kwargs)

        amount = self.request.POST.get('amount', None)
        if not amount:
            if _messages:
                messages.add_message(self.request, messages.ERROR, _('Amount field can not be blank'))
            return super(WalletsWithdrawView, self).post(request, *args, **kwargs)

        obj = self.get_object()

        if float(amount) > obj.balance:
            if _messages:
                messages.add_message(self.request, messages.ERROR, _('Amount can not be more than the balance of this address.'))
            return super(WalletsWithdrawView, self).post(request, *args, **kwargs)

        try:
            transaction = obj.spend(address, float(amount))
            if _messages:
                messages.add_message(self.request, messages.SUCCESS, _('Transaction successfully created {}'.format(transaction)))
        except:
            if _messages:
                messages.add_message(self.request, messages.ERROR, _('Something wrong, try again later'))
        return super(WalletsWithdrawView, self).post(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        return redirect(
            reverse('wallets:detail', kwargs={
                'wallet': self.kwargs['wallet'],
                'address': self.kwargs['address']
                }
            )
        )
'''

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
        try:
            signature = kwargs['signature']
            sign = decode_signin(signature)
            validate_signin(sign)
            get_webhook.send(
                sender=None,
                from_address = sign['from_address'],
                to_addresses = sign['to_addresses'],
                symbol = sign['symbol'],
                event = sign['event'],
                transaction_id = sign['transaction_id'],
                payload = sign['payload']
            )
            webhook_id = extract_webhook_id(signature, sign['symbol'])
            if webhook_id:
                unsubscribe = unsubscribe_from_webhook(webhook_id, sign['symbol'])
        except BadSignature:
            pass
        except SignatureExpired:
            pass
        return JsonResponse({}, status=200)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(WalletsWebhookView, self).dispatch(request, *args, **kwargs)


class InvoiceListView(LoginRequiredMixin, TemplateView):

    template_name = 'wallets/invoice_list.html'

    def get_context_data(self, **kwargs):
        context = super(InvoiceListView, self).get_context_data(**kwargs)
        for symbol in ['btc', 'ltc', 'dash', 'doge']:
            wallet = get_wallet_model(symbol)
            wallets = wallet.objects.filter(user = self.request.user).all()
            invoices_list = get_wallet_invoices(
                invoices = Invoice.objects.all(),
                wallets = wallets,
                symbol = symbol
            )
            context['{}_received_invoices'.format(symbol)] = invoices_list['{}_received_invoices'.format(symbol)]
            context['{}_sended_invoices'.format(symbol)] = invoices_list['{}_sended_invoices'.format(symbol)]
        return context


class InvoiceDetailView(LoginRequiredMixin, DetailView):

    model = Invoice

    def get_object(self, *args, **kwargs):
        obj = super(InvoiceDetailView, self).get_object(*args, **kwargs)
        if obj.sender_wallet_object.user != self.request.user:
            raise PermissionDenied()
        elif self.request.user not in [wallet.user for wallet in obj.receiver_wallet_object.all()]:
            raise PermissionDenied()
        else:
            return obj


class InvoicePayView(LoginRequiredMixin, DetailView):
    
    model = Invoice

    def dispatch(self, request, *args, **kwargs):
        invoice = get_object_or_404(Invoice, pk=self.kwargs['pk'])
        if invoice.sender_wallet_object.user != request.user:
            raise PermissionDenied()
        invoice.pay()
        redirect(reverse('wallets:invoice_detail', kwargs={'pk': invoice.pk}))
        return super(InvoicePayView, self).dispatch(request, *args, **kwargs)