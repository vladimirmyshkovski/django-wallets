from django.conf import settings
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.http import JsonResponse, Http404
from django.urls import reverse  # , reverse_lazy
#from django.shortcuts import redirect
from django.views.generic import (DetailView, ListView, RedirectView,
                                  View, TemplateView, DeleteView)
from django.views.generic.edit import FormMixin
from django.views.decorators.csrf import csrf_exempt
#from django.shortcuts import get_object_or_404
from .utils import (get_wallet_model, decode_signin,
                    extract_webhook_id, unsubscribe_from_webhook,
                    validate_signin, to_satoshi)
from .signals import get_webhook
from .mixins import OwnerPermissionsMixin, CheckWalletMixin
from .models import Invoice
from .forms import WithdrawForm, PayForm
from .services import generate_new_address
from django.core.signing import BadSignature, SignatureExpired
from guardian.mixins import PermissionRequiredMixin, LoginRequiredMixin


try:
    _messages = 'django.contrib.messages' in settings.INSTALLED_APPS

except AttributeError:  # pragma: no cover
    _messages = False

if _messages:  # pragma: no cover
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
            user=request.user,
            coin_symbol=self.kwargs['wallet']
        )
        self.address = address
        if address:
            if _messages:  # pragma: no cover
                messages.success(
                    self.request,
                    _('New {} address successfully created'.format(
                        address.coin_symbol.upper()
                    ))
                )
        else:
            if _messages:  # pragma: no cover
                messages.error(
                    self.request,
                    _('Something wrong, try again later')
                )
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
        context['form'] = self.get_form()
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
                data=self.request.POST,
                obj=self.object
            )
        else:
            return self.form_class

    def form_valid(self, form):
        transaction = form.spend()
        if _messages:  # pragma: no cover
            messages.success(
                self.request,
                _('Transaction successfully created {}'.format(transaction))
            )
        return super(WalletsDetailView, self).form_valid(form)

    def get_success_url(self):
        return reverse(
            'wallets:detail',
            kwargs={
                'wallet': self.kwargs['wallet'],
                'address': self.kwargs['address']
            })


class WalletsWebhookView(View):
    http_method_names = [u'post']

    def post(self, request, *args, **kwargs):
        print('HELLO')
        try:
            signature = kwargs['signature']
            sign = decode_signin(signature)
            print('PAYLOAD IS: ' + str(sign['payload']))
            validate_signin(sign)
            print('IS VALID')
            get_webhook.send(
                sender=None,
                from_address=sign['from_address'],
                to_addresses=sign['to_addresses'],
                symbol=sign['symbol'],
                event=sign['event'],
                transaction_id=sign['transaction_id'],
                payload=sign['payload']
            )
            print("SIGNAL SENT")
            webhook_id = extract_webhook_id(signature, sign['symbol'])
            print('WEBHOOK ID: ' + str(webhook_id))
            if webhook_id:
                unsubscribe_from_webhook(
                    webhook_id, sign['symbol']
                )
        except:
            return JsonResponse({}, status=200)    
        #except BadSignature:
        #    pass
        #except SignatureExpired:
        #    pass
        return JsonResponse({}, status=200)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(WalletsWebhookView, self).dispatch(
            request, *args, **kwargs
        )


class InvoiceListView(LoginRequiredMixin, TemplateView):

    template_name = 'wallets/invoice_list.html'

    def get_context_data(self, **kwargs):
        context = super(InvoiceListView, self).get_context_data(**kwargs)
        symbols = ['btc', 'ltc', 'dash', 'doge', 'bcy']
        context['symbols'] = symbols
        for symbol in symbols:
            wallet = get_wallet_model(symbol)
            received_invoices = wallet.get_received_invoices(
                user=self.request.user,
                symbol=symbol
            )
            context['{}_received_invoices'.format(symbol)] = received_invoices
            sended_invoices = wallet.get_sended_invoices(
                user=self.request.user,
                symbol=symbol
            )
            context['{}_sended_invoices'.format(symbol)] = sended_invoices
            context['form'] = PayForm
            '''
            wallets = wallet.objects.filter(user=self.request.user).all()
            invoices_list = get_wallet_invoices(
                invoices=Invoice.objects.all(),
                wallets=wallets,
                symbol=symbol
            )
            received_invoices = '{}_received_invoices'.format(symbol)
            sended_invoices = '{}_sended_invoices'.format(symbol)
            context[received_invoices] = invoices_list[received_invoices]
            context[sended_invoices] = invoices_list[sended_invoices]
            context['len_{}'.format(received_invoices)] = 0
            context['len_{}'.format(sended_invoices)] = 0

            for invoice in invoices_list[received_invoices]:
                if not invoice.is_paid:
                    context['len_{}'.format(received_invoices)] += 1
            for invoice in invoices_list[sended_invoices]:
                if not invoice.is_paid:
                    context['len_{}'.format(sended_invoices)] += 1
            '''
        return context


class InvoiceDetailView(LoginRequiredMixin, PermissionRequiredMixin,
                        FormMixin, DetailView):

    model = Invoice
    permission_required = ['wallets.view_invoice']
    raise_exception = True
    form_class = PayForm
    initial = {'payload': ''}

    def get_form(self):
        if self.request.POST:
            return self.form_class(data=self.request.POST)
        else:
            return self.form_class

    def get_context_data(self, **kwargs):
        context = super(InvoiceDetailView, self).get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context

    def form_valid(self, form):
        self.payload = form.cleaned_data['payload']

        if self.request.user.has_perm('pay_invoice', self.object):
            amounts_sum = sum(self.object.amount)
            balance = to_satoshi(
                float(self.object.sender_wallet_object.balance)
            )

            if self.object.is_expired:
                if _messages:
                    messages.error(self.request, _('Invoice expired'))

            if balance >= amounts_sum:
                payload = self.payload
                try:
                    self.object.pay(payload)
                    if _messages:
                        last_tx_ref = self.object.tx_refs.last()
                        transaction = last_tx_ref.tx_ref
                        messages.success(
                            self.request,
                            _('''The account was successfully sent.
                                 Wait for transaction {}
                                confirmation.'''.format(transaction))
                        )
                except:
                    if _messages:
                        messages.error(
                            self.request,
                            _('Something went wrong. Try again later')
                        )
            else:
                if _messages:
                    messages.error(
                        self.request,
                        _('''You do not have enough funds
                             to pay your invoice.''')
                    )
        return super(InvoiceDetailView, self).form_valid(form)

    def post(self, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse(
            'wallets:invoice_detail',
            kwargs={'pk': self.object.pk}
        )


class InvoiceDeleteView(LoginRequiredMixin, PermissionRequiredMixin,
                        DeleteView):

    model = Invoice
    permission_required = ['wallets.pay_invoice']
    raise_exception = True

"""
class InvoicePayView(LoginRequiredMixin,
                     PermissionRequiredMixin,
                     FormMixin, View):

    model = Invoice
    permission_required = ['wallets.pay_invoice']
    raise_exception = True
    form_class = PayForm
    http_method_names = ['post']

    #def get(self, *args, kwargs):
    #    return super(InvoicePayView, self).get(*args, **kwargs)

    def get_form(self):
        return self.form_class(data=self.request.POST)

    def form_valid(self, form):
        self.payload = form.cleaned_data['payload']
        return super(WalletsDetailView, self).form_valid(form)

    def post(self, *args, **kwargs):
        invoice = get_object_or_404(Invoice, pk=self.kwargs['pk'])
        form = self.get_form()
        if form.is_valid():
            self.payload = form.cleaned_data['payload']

            if self.request.user.has_perm('pay_invoice', invoice):
                amounts_sum = sum(invoice.amount)
                balance = to_satoshi(
                    float(invoice.sender_wallet_object.balance)
                )

            if invoice.is_expired:
                if _messages:
                    messages.error(self.request, _('Invoice expired'))

            if balance >= amounts_sum:
                payload = self.payload
                invoice.pay(payload)
                if _messages:
                    last_tx_ref = invoice.tx_refs.last()
                    transaction = last_tx_ref.tx_ref
                    messages.success(
                        self.request,
                        _('''The account was successfully sent.
                             Wait for transaction {}
                             confirmation.'''.format(transaction))
                    )
            else:
                if _messages:
                    messages.error(
                        self.request,
                        _('''You do not have enough funds
                             to pay your invoice.''')
                    )
            redirect(
                reverse('wallets:invoice_detail', kwargs={'pk': invoice.pk})
            )
        else:
            self.form_invalid(form)
        return super(InvoicePayView, self).post(*args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        #invoice = get_object_or_404(Invoice, pk=self.kwargs['pk'])
        return super(InvoicePayView, self).dispatch(request, *args, **kwargs)
"""
