from guardian.mixins import PermissionRequiredMixin, LoginRequiredMixin

from django.conf import settings
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.http import JsonResponse, Http404
from django.urls import reverse
from django.shortcuts import redirect
from django.views.generic.edit import FormMixin
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import (DetailView, ListView, RedirectView,
                                  View, TemplateView, DeleteView)
from django.shortcuts import get_object_or_404

from .utils import (decode_signin, extract_webhook_id,
                    unsubscribe_from_webhook,
                    validate_signin, to_satoshi,
                    get_wallet_model)
from .signals import get_webhook
from .mixins import OwnerPermissionsMixin, CheckWalletMixin
from .models import Invoice, Payment
from .forms import WithdrawForm
from .services import generate_new_address
from .queries import (get_payments, get_invoices,
                      get_user_wallet_balance,
                      get_user_wallet_balance_usd)

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
        context['symbols'] = ['btc', 'ltc', 'dash', 'doge']
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
        context['total_balance'] = get_user_wallet_balance(
            user=self.request.user,
            symbol=self.kwargs['wallet']
        )
        context['total_balance_usd'] = get_user_wallet_balance_usd(
            user=self.request.user,
            symbol=self.kwargs['wallet']
        )
        context['symbol'] = self.kwargs['wallet']
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
        try:
            signature = kwargs['signature']
            sign = decode_signin(signature)
            validate_signin(sign)
            get_webhook.send(
                sender=None,
                from_address=sign['from_address'],
                to_addresses=sign['to_addresses'],
                symbol=sign['symbol'],
                event=sign['event'],
                transaction_id=sign['transaction_id'],
                invoice_id=sign['invoice_id'],
                content_object=sign['content_object']
            )
            data = extract_webhook_id(signature, sign['symbol'])
            if data:
                unsubscribe_from_webhook(
                    api_key=data['api_key'],
                    webhook_id=data['webhook_id'],
                    coin_symbol=sign['symbol'],
                    can_unsubscribe=data['can_unsubscribe']
                )
        except Exception:
            pass
        finally:
            return JsonResponse({}, status=200)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(WalletsWebhookView, self).dispatch(
            request, *args, **kwargs
        )


class InvoiceListView(LoginRequiredMixin, CheckWalletMixin, TemplateView):

    template_name = 'wallets/invoice_list.html'

    def get_context_data(self, **kwargs):
        context = super(InvoiceListView, self).get_context_data(**kwargs)
        if self.model:
            context['invoices'] = get_invoices(
                user=self.request.user,
                symbol=self.symbol
            )
            context['payments'] = get_payments(
                user=self.request.user,
                symbol=self.symbol
            )
            context['symbol'] = self.symbol
        return context

    def dispatch(self, request, *args, **kwargs):
        self.symbol = self.kwargs['wallet']
        self.model = self.check_wallet(self.symbol)
        return super(InvoiceListView, self).dispatch(
            request, *args, **kwargs
        )


class InvoiceDetailView(LoginRequiredMixin, PermissionRequiredMixin,
                        DetailView):

    model = Invoice
    permission_required = ['wallets.view_invoice']
    raise_exception = True

    #def get_context_data(self, **kwargs):
    #    context = super(InvoiceDetailView, self).get_context_data(**kwargs)
    #    return context
    """
    def post(self, *args, **kwargs):
        self.object = self.get_object()

        if self.request.user.has_perm('pay_invoice', self.object):
            balance = to_satoshi(float(self.object.wallet.balance))

            if self.object.is_expired:
                if _messages:
                    messages.error(self.request, _('Invoice expired'))

            if balance >= self.object.amount:
                try:
                    self.object.pay()
                    if _messages:
                        messages.success(
                            self.request,
                            _('''The account was successfully sent.
                                 Wait for transaction {}
                                confirmation.'''.format(self.object.tx_ref))
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
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse(
            'wallets:invoice_detail',
            kwargs={'pk': self.object.pk}
        )
    """


class InvoicePayView(LoginRequiredMixin, PermissionRequiredMixin,
                     DetailView):

    model = Invoice
    permission_required = [
        'wallets.view_invoice',
        'wallets.pay_invoice'
    ]
    raise_exception = True
    template_name = 'wallets/invoice_confirm_pay.html'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.request.user.has_perm('pay_invoice', self.object):
            balance = to_satoshi(float(self.object.wallet.balance))

            if self.object.is_expired:
                if _messages:
                    messages.error(self.request, _('Invoice expired'))

            if balance >= self.object.amount:
                try:
                    self.object.pay()
                    if _messages:
                        messages.success(
                            self.request,
                            _('''The account was successfully sent.
                                 Wait for transaction {}
                                confirmation.'''.format(self.object.tx_ref))
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

        return redirect(self.get_success_url())

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

    def get_success_url(self):
        return reverse(
            'wallets:invoice_list',
            kwargs={'wallet': self.object.wallet.coin_symbol}
        )


class PaymentListView(LoginRequiredMixin, ListView):

    model = Payment
    paginate_by = 10

    def get_queryset(self):
        queryset = super(PaymentListView, self).get_queryset()
        qs = []
        for symbol in ['btc', 'ltc', 'dash', 'doge', 'bcy']:
            wallet_model = get_wallet_model(symbol)
            if wallet_model:
                wallets = wallet_model.objects.filter(user=self.request.user)
                for wallet in wallets:
                    for payment in wallet.payments.all():
                        if self.request.user.has_perm('view_payment', payment):
                            qs.append(payment.id)
            else:
                return []
        return queryset.filter(id__in=qs)
