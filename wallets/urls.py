from django.urls import re_path
from . import views

app_name = 'wallets'
urlpatterns = [
    #re_path(
    #    r'autocomplete/',
    #    view=views.WalletsAutocompleteView.as_view(),
    #    name='autocomplete'
    #),
    re_path(
        r'^$',
        view=views.AllUserWalletsList.as_view(),
        name='all'
    ),
    re_path(
        r'^webhook/(?P<signature>.*)/$',
        view=views.WalletsWebhookView.as_view(),
        name='webhook'
    ),
    re_path(
        r'^payments/',
        view=views.PaymentListView.as_view(),
        name='payment_list'
    ),
    re_path(
        r'^invoices/(?P<wallet>[\w.@+-]+)/$',
        view=views.InvoiceListView.as_view(),
        name='invoice_list'
    ),
    re_path(
        r'^invoices/(?P<pk>\d+)/_detail/$',
        view=views.InvoiceDetailView.as_view(),
        name='invoice_detail'
    ),
    #re_path(
    #    r'^invoices/(?P<pk>\d+)/_pay/$',
    #    view=views.InvoicePayView.as_view(),
    #    name='invoice_pay'
    #),
    re_path(
        r'^invoices/(?P<pk>\d+)/_delete/$',
        view=views.InvoiceDeleteView.as_view(),
        name='invoice_delete'
    ),
    re_path(
        r'^(?P<wallet>[\w.@+-]+)/$',
        view=views.WalletsListView.as_view(),
        name='list'
    ),
    re_path(
        r'^(?P<wallet>[\w.@+-]+)/_create/$',
        view=views.WalletsCreateView.as_view(),
        name='create'
    ),
    re_path(
        r'^(?P<wallet>[\w.@+-]+)/(?P<address>[\w.@+-]+)/_detail/$',
        view=views.WalletsDetailView.as_view(),
        name='detail'
    ),
    #re_path(
    #    r'^(?P<wallet>[\w.@+-]+)/(?P<address>[\w.@+-]+)/_withdraw/$',
    #    view=views.WalletsWithdrawView.as_view(),
    #    name='withdraw'
    #),
]
