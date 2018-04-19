# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.conf.urls import url, include

from wallets.urls import urlpatterns as wallets_urls

urlpatterns = [
    url(r'^wallets/', include((wallets_urls, 'wallets'), namespace='wallets')),
]
