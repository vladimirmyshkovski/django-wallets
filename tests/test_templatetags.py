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
        }
        ))

        self.assertEqual(
            out,
            '5'
        )


class TestUnpaidUserReceivedInvoices(TestCase):

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

        btc_invoice = factories.BtcInvoiceFactory(sender_wallet_object=btc)
        ltc_invoice = factories.LtcInvoiceFactory(sender_wallet_object=ltc)
        dash_invoice = factories.DashInvoiceFactory(sender_wallet_object=dash)
        doge_invoice = factories.DogeInvoiceFactory(sender_wallet_object=doge)
        bcy_invoice = factories.BcyInvoiceFactory(sender_wallet_object=bcy)

        btc_invoice.receiver_wallet_object.add(btc)
        btc_invoice.save()
        ltc_invoice.receiver_wallet_object.add(ltc)
        ltc_invoice.save()
        dash_invoice.receiver_wallet_object.add(dash)
        dash_invoice.save()
        bcy_invoice.receiver_wallet_object.add(doge)
        doge_invoice.save()
        bcy_invoice.receiver_wallet_object.add(bcy)
        bcy_invoice.save()

        request_factory = RequestFactory()
        request = request_factory.get('/')
        request.user = self.user

        out = Template(
            "{% load wallets_tags %}"
            "{% unpaid_user_received_invoices %}"
        ).render(Context({
            'request': request,
        }
        ))

        self.assertEqual(
            out,
            '5'
        )


class TestUnpaidUserInvoices(TestCase):

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

        btc_invoice = factories.BtcInvoiceFactory(sender_wallet_object=btc)
        ltc_invoice = factories.LtcInvoiceFactory(sender_wallet_object=ltc)
        dash_invoice = factories.DashInvoiceFactory(sender_wallet_object=dash)
        doge_invoice = factories.DogeInvoiceFactory(sender_wallet_object=doge)
        bcy_invoice = factories.BcyInvoiceFactory(sender_wallet_object=bcy)

        btc_invoice.receiver_wallet_object.add(btc)
        btc_invoice.save()
        ltc_invoice.receiver_wallet_object.add(ltc)
        ltc_invoice.save()
        dash_invoice.receiver_wallet_object.add(dash)
        dash_invoice.save()
        bcy_invoice.receiver_wallet_object.add(doge)
        doge_invoice.save()
        bcy_invoice.receiver_wallet_object.add(bcy)
        bcy_invoice.save()

        request_factory = RequestFactory()
        request = request_factory.get('/')
        request.user = self.user

        out = Template(
            "{% load wallets_tags %}"
            "{% unpaid_user_invoices %}"
        ).render(Context({
            'request': request,
        }
        ))

        self.assertEqual(
            out,
            '10'
        )


class TestUnpaidSymbolUserSendedInvoices(TestCase):

    def setUp(self):
        self.user = self.make_user('user-{}'.format(random.randint(1, 100)))

    def test_without_invoices(self):
        request_factory = RequestFactory()
        request = request_factory.get('/')
        request.user = self.user

        out = Template(
            "{% load wallets_tags %}"
            "{% unpaid_symbol_user_sended_invoices symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'btc'
        }
        ))

        self.assertEqual(
            out,
            '0'
        )

        out = Template(
            "{% load wallets_tags %}"
            "{% unpaid_symbol_user_sended_invoices symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'ltc'
        }
        ))

        self.assertEqual(
            out,
            '0'
        )

        out = Template(
            "{% load wallets_tags %}"
            "{% unpaid_symbol_user_sended_invoices symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'dash'
        }
        ))

        self.assertEqual(
            out,
            '0'
        )

        out = Template(
            "{% load wallets_tags %}"
            "{% unpaid_symbol_user_sended_invoices symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'doge'
        }
        ))

        self.assertEqual(
            out,
            '0'
        )

        out = Template(
            "{% load wallets_tags %}"
            "{% unpaid_symbol_user_sended_invoices symbol %}"
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
        request_factory = RequestFactory()
        request = request_factory.get('/')
        request.user = self.user

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

        out = Template(
            "{% load wallets_tags %}"
            "{% unpaid_symbol_user_sended_invoices symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'btc'
        }
        ))

        self.assertEqual(
            out,
            '1'
        )

        out = Template(
            "{% load wallets_tags %}"
            "{% unpaid_symbol_user_sended_invoices symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'ltc'
        }
        ))

        self.assertEqual(
            out,
            '1'
        )

        out = Template(
            "{% load wallets_tags %}"
            "{% unpaid_symbol_user_sended_invoices symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'dash'
        }
        ))

        self.assertEqual(
            out,
            '1'
        )

        out = Template(
            "{% load wallets_tags %}"
            "{% unpaid_symbol_user_sended_invoices symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'doge'
        }
        ))

        self.assertEqual(
            out,
            '1'
        )

        out = Template(
            "{% load wallets_tags %}"
            "{% unpaid_symbol_user_sended_invoices symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'bcy'
        }
        ))

        self.assertEqual(
            out,
            '1'
        )


class TestUnpaidSymbolUserReceivedInvoices(TestCase):

    def setUp(self):
        self.user = self.make_user('user-{}'.format(random.randint(1, 100)))

    def test_without_invoices(self):
        request_factory = RequestFactory()
        request = request_factory.get('/')
        request.user = self.user

        out = Template(
            "{% load wallets_tags %}"
            "{% unpaid_symbol_user_received_invoices symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'btc'
        }
        ))

        self.assertEqual(
            out,
            '0'
        )

        out = Template(
            "{% load wallets_tags %}"
            "{% unpaid_symbol_user_received_invoices symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'ltc'
        }
        ))

        self.assertEqual(
            out,
            '0'
        )

        out = Template(
            "{% load wallets_tags %}"
            "{% unpaid_symbol_user_received_invoices symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'dash'
        }
        ))

        self.assertEqual(
            out,
            '0'
        )

        out = Template(
            "{% load wallets_tags %}"
            "{% unpaid_symbol_user_received_invoices symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'doge'
        }
        ))

        self.assertEqual(
            out,
            '0'
        )

        out = Template(
            "{% load wallets_tags %}"
            "{% unpaid_symbol_user_received_invoices symbol %}"
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
        request_factory = RequestFactory()
        request = request_factory.get('/')
        request.user = self.user

        btc = factories.BtcFactory(user=self.user)
        ltc = factories.LtcFactory(user=self.user)
        dash = factories.DashFactory(user=self.user)
        doge = factories.DogeFactory(user=self.user)
        bcy = factories.BcyFactory(user=self.user)

        btc_invoice = factories.BtcInvoiceFactory(sender_wallet_object=btc)
        ltc_invoice = factories.LtcInvoiceFactory(sender_wallet_object=ltc)
        dash_invoice = factories.DashInvoiceFactory(sender_wallet_object=dash)
        doge_invoice = factories.DogeInvoiceFactory(sender_wallet_object=doge)
        bcy_invoice = factories.BcyInvoiceFactory(sender_wallet_object=bcy)

        btc_invoice.receiver_wallet_object.add(btc)
        btc_invoice.save()
        ltc_invoice.receiver_wallet_object.add(ltc)
        ltc_invoice.save()
        dash_invoice.receiver_wallet_object.add(dash)
        dash_invoice.save()
        bcy_invoice.receiver_wallet_object.add(doge)
        doge_invoice.save()
        bcy_invoice.receiver_wallet_object.add(bcy)
        bcy_invoice.save()

        out = Template(
            "{% load wallets_tags %}"
            "{% unpaid_symbol_user_received_invoices symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'btc'
        }
        ))

        self.assertEqual(
            out,
            '1'
        )

        out = Template(
            "{% load wallets_tags %}"
            "{% unpaid_symbol_user_received_invoices symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'ltc'
        }
        ))

        self.assertEqual(
            out,
            '1'
        )

        out = Template(
            "{% load wallets_tags %}"
            "{% unpaid_symbol_user_received_invoices symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'dash'
        }
        ))

        self.assertEqual(
            out,
            '1'
        )

        out = Template(
            "{% load wallets_tags %}"
            "{% unpaid_symbol_user_received_invoices symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'doge'
        }
        ))

        self.assertEqual(
            out,
            '1'
        )

        out = Template(
            "{% load wallets_tags %}"
            "{% unpaid_symbol_user_received_invoices symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'bcy'
        }
        ))

        self.assertEqual(
            out,
            '1'
        )


class TestUnpaidSymbolUserInvoices(TestCase):

    def setUp(self):
        self.user = self.make_user('user-{}'.format(random.randint(1, 100)))

    def test_without_invoices(self):
        request_factory = RequestFactory()
        request = request_factory.get('/')
        request.user = self.user

        out = Template(
            "{% load wallets_tags %}"
            "{% unpaid_symbol_user_invoices symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'btc'
        }
        ))

        self.assertEqual(
            out,
            '0'
        )

        out = Template(
            "{% load wallets_tags %}"
            "{% unpaid_symbol_user_invoices symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'ltc'
        }
        ))

        self.assertEqual(
            out,
            '0'
        )

        out = Template(
            "{% load wallets_tags %}"
            "{% unpaid_symbol_user_invoices symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'dash'
        }
        ))

        self.assertEqual(
            out,
            '0'
        )

        out = Template(
            "{% load wallets_tags %}"
            "{% unpaid_symbol_user_invoices symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'doge'
        }
        ))

        self.assertEqual(
            out,
            '0'
        )

        out = Template(
            "{% load wallets_tags %}"
            "{% unpaid_symbol_user_invoices symbol %}"
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
        request_factory = RequestFactory()
        request = request_factory.get('/')
        request.user = self.user

        btc = factories.BtcFactory(user=self.user)
        ltc = factories.LtcFactory(user=self.user)
        dash = factories.DashFactory(user=self.user)
        doge = factories.DogeFactory(user=self.user)
        bcy = factories.BcyFactory(user=self.user)

        btc_invoice = factories.BtcInvoiceFactory(sender_wallet_object=btc)
        ltc_invoice = factories.LtcInvoiceFactory(sender_wallet_object=ltc)
        dash_invoice = factories.DashInvoiceFactory(sender_wallet_object=dash)
        doge_invoice = factories.DogeInvoiceFactory(sender_wallet_object=doge)
        bcy_invoice = factories.BcyInvoiceFactory(sender_wallet_object=bcy)

        btc_invoice.receiver_wallet_object.add(btc)
        btc_invoice.save()
        ltc_invoice.receiver_wallet_object.add(ltc)
        ltc_invoice.save()
        dash_invoice.receiver_wallet_object.add(dash)
        dash_invoice.save()
        bcy_invoice.receiver_wallet_object.add(doge)
        doge_invoice.save()
        bcy_invoice.receiver_wallet_object.add(bcy)
        bcy_invoice.save()

        out = Template(
            "{% load wallets_tags %}"
            "{% unpaid_symbol_user_invoices symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'btc'
        }
        ))

        self.assertEqual(
            out,
            '2'
        )

        out = Template(
            "{% load wallets_tags %}"
            "{% unpaid_symbol_user_invoices symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'ltc'
        }
        ))

        self.assertEqual(
            out,
            '2'
        )

        out = Template(
            "{% load wallets_tags %}"
            "{% unpaid_symbol_user_invoices symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'dash'
        }
        ))

        self.assertEqual(
            out,
            '2'
        )

        out = Template(
            "{% load wallets_tags %}"
            "{% unpaid_symbol_user_invoices symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'doge'
        }
        ))

        self.assertEqual(
            out,
            '2'
        )

        out = Template(
            "{% load wallets_tags %}"
            "{% unpaid_symbol_user_invoices symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'bcy'
        }
        ))

        self.assertEqual(
            out,
            '2'
        )
