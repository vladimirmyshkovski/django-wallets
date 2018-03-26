from django.urls import re_path
from django.views.generic import TemplateView
from . import views

app_name = 'wallets'
urlpatterns = [
    #re_path(
    #    r'autocomplete/',
    #    view=views.WalletsAutocompleteView.as_view(),
    #    name='autocomplete'
    #),
    re_path(
        r'webhook/(?P<signature>.*)/$',
        view=views.WalletsWebhookView.as_view(),
        name='webhook'
    ),
    re_path(
        r'(?P<wallet>[\w.@+-]+)/(?P<address>[\w.@+-]+)/$',
        view=views.WalletsDetailView.as_view(),
        name='detail'
    ),
    re_path(
        r'(?P<wallet>[\w.@+-]+)/(?P<address>[\w.@+-]+)/~withdraw/$',
        view=views.WalletsWithdrawView.as_view(),
        name='withdraw'
    ),    
    re_path(
        r'(?P<wallet>[\w.@+-]+)/$',
        view=views.WalletsListView.as_view(),
        name='list'
    ),
    re_path(
        r'(?P<wallet>[\w.@+-]+)/$',
        view=views.WalletsCreateView.as_view(),
        name='create'
    ),
]