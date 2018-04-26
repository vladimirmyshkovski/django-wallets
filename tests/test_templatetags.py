from test_plus.test import TestCase
from . import factories
from django.test import RequestFactory
import random
from django.template import Context, Template


class TestUnpaidUserSendedInvoices(TestCase):

    def setUp(self):
        self.user = self.make_user('user-{}'.format(random.randint(1, 100)))

    def test_without_invoices(self):
        request_factory = RequestFactory()
        request = request_factory.get('/')
        request.user = self.user

        out = Template(
            "{% load wallets_tags %}"
            "{% unpaid_user_sended_invoices %}"
        ).render(Context({
            'request': request,
            'symbol': 'bcy'
            }
        ))

        self.assertEqual(
            out,
            '0'
        )

    def test_with_invoices(self):
        btc = factories.BtcFactory(user=self.user)
        ltc = factories.LtcFactory(user=self.user)
        dash = factories.DashFactory(user=self.user)
        doge = factories.DogeFactory(user=self.user)
        bcy = factories.BcyFactory(user=self.user)
        
        factories.BtcInvoiceFactory(sender_wallet_object=btc)
        factories.LtcInvoiceFactory(sender_wallet_object=ltc)
        factories.DashInvoiceFactory(sender_wallet_object=dash)
        factories.DogeInvoiceFactory(sender_wallet_object=doge)
        factories.BcyInvoiceFactory(sender_wallet_object=bcy)

        request_factory = RequestFactory()
        request = request_factory.get('/')
        request.user = self.user

        out = Template(
            "{% load wallets_tags %}"
            "{% unpaid_user_sended_invoices %}"
        ).render(Context({
            'request': request,
            'symbol': 'bcy'
            }
        ))

        self.assertEqual(
            out,
            '4'
        )
