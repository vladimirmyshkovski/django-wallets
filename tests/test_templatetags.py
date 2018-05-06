#from test_plus.test import TestCase
#from . import factories
#from django.test import RequestFactory
#import random
#from django.template import Context, Template

'''
class TestCountUnpaidInvoices(TestCase):

    def setUp(self):
        self.user = self.make_user('user-{}'.format(random.randint(1, 100)))

    def test_without_invoices(self):
        request_factory = RequestFactory()
        request = request_factory.get('/')
        request.user = self.user

        out = Template(
            "{% load wallets %}"
            "{% count_unpaid_invoices %}"
        ).render(Context({
            'request': request,
            })
        )

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

        factories.BtcInvoiceFactory(wallet=btc)
        factories.LtcInvoiceFactory(wallet=ltc)
        factories.DashInvoiceFactory(wallet=dash)
        factories.DogeInvoiceFactory(wallet=doge)
        factories.BcyInvoiceFactory(wallet=bcy)

        request_factory = RequestFactory()
        request = request_factory.get('/')
        request.user = self.user

        out = Template(
            "{% load wallets %}"
            "{% count_unpaid_invoices %}"
        ).render(Context({
            'request': request,
            })
        )

        self.assertEqual(
            out,
            '5'
        )


class TestCountUnpaidPayments(TestCase):

    def setUp(self):
        self.user = self.make_user('user-{}'.format(random.randint(1, 100)))

    def test_without_invoices(self):
        request_factory = RequestFactory()
        request = request_factory.get('/')
        request.user = self.user

        out = Template(
            "{% load wallets %}"
            "{% count_unpaid_payments %}"
        ).render(Context({
            'request': request,
            })
        )

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

        btc_invoice = factories.BtcInvoiceFactory(wallet=btc)
        ltc_invoice = factories.LtcInvoiceFactory(wallet=ltc)
        dash_invoice = factories.DashInvoiceFactory(wallet=dash)
        doge_invoice = factories.DogeInvoiceFactory(wallet=doge)
        bcy_invoice = factories.BcyInvoiceFactory(wallet=bcy)
        factories.PaymentBtcInvoiceFactory(
            invoice=btc_invoice,
            wallet=btc
        )
        factories.PaymentLtcInvoiceFactory(
            invoice=ltc_invoice,
            wallet=ltc
        )
        factories.PaymentDashInvoiceFactory(
            invoice=dash_invoice,
            wallet=dash
        )
        factories.PaymentDogeInvoiceFactory(
            invoice=doge_invoice,
            wallet=doge
        )
        factories.PaymentBcyInvoiceFactory(
            invoice=bcy_invoice,
            wallet=bcy
        )

        request_factory = RequestFactory()
        request = request_factory.get('/')
        request.user = self.user

        out = Template(
            "{% load wallets %}"
            "{% count_unpaid_payments %}"
        ).render(Context({
            'request': request,
            })
        )

        self.assertEqual(
            out,
            '5'
        )


class TestCountUnpaid(TestCase):

    def setUp(self):
        self.user = self.make_user('user-{}'.format(random.randint(1, 100)))

    def test_without_invoices(self):
        request_factory = RequestFactory()
        request = request_factory.get('/')
        request.user = self.user

        out = Template(
            "{% load wallets %}"
            "{% count_unpaid %}"
        ).render(Context({
            'request': request,
            })
        )

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

        btc_invoice = factories.BtcInvoiceFactory(wallet=btc)
        ltc_invoice = factories.LtcInvoiceFactory(wallet=ltc)
        dash_invoice = factories.DashInvoiceFactory(wallet=dash)
        doge_invoice = factories.DogeInvoiceFactory(wallet=doge)
        bcy_invoice = factories.BcyInvoiceFactory(wallet=bcy)
        factories.PaymentBtcInvoiceFactory(
            invoice=btc_invoice,
            wallet=btc
        )
        factories.PaymentLtcInvoiceFactory(
            invoice=ltc_invoice,
            wallet=ltc
        )
        factories.PaymentDashInvoiceFactory(
            invoice=dash_invoice,
            wallet=dash
        )
        factories.PaymentDogeInvoiceFactory(
            invoice=doge_invoice,
            wallet=doge
        )
        factories.PaymentBcyInvoiceFactory(
            invoice=bcy_invoice,
            wallet=bcy
        )

        request_factory = RequestFactory()
        request = request_factory.get('/')
        request.user = self.user

        out = Template(
            "{% load wallets %}"
            "{% count_unpaid %}"
        ).render(Context({
            'request': request,
            })
        )

        self.assertEqual(
            out,
            '10'
        )


class TestCountUnpaidSymbolInvoices(TestCase):

    def setUp(self):
        self.user = self.make_user('user-{}'.format(random.randint(1, 100)))

    def test_without_invoices(self):
        request_factory = RequestFactory()
        request = request_factory.get('/')
        request.user = self.user

        out = Template(
            "{% load wallets %}"
            "{% count_unpaid_symbol_invoices symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'btc'
            })
        )

        self.assertEqual(
            out,
            '0'
        )

        out = Template(
            "{% load wallets %}"
            "{% count_unpaid_symbol_invoices symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'ltc'
            })
        )

        self.assertEqual(
            out,
            '0'
        )

        out = Template(
            "{% load wallets %}"
            "{% count_unpaid_symbol_invoices symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'dash'
            })
        )

        self.assertEqual(
            out,
            '0'
        )

        out = Template(
            "{% load wallets %}"
            "{% count_unpaid_symbol_invoices symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'doge'
            })
        )

        self.assertEqual(
            out,
            '0'
        )

        out = Template(
            "{% load wallets %}"
            "{% count_unpaid_symbol_invoices symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'bcy'
            })
        )

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

        factories.BtcInvoiceFactory(wallet=btc)
        factories.LtcInvoiceFactory(wallet=ltc)
        factories.DashInvoiceFactory(wallet=dash)
        factories.DogeInvoiceFactory(wallet=doge)
        factories.BcyInvoiceFactory(wallet=bcy)

        out = Template(
            "{% load wallets %}"
            "{% count_unpaid_symbol_invoices symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'btc'
            })
        )

        self.assertEqual(
            out,
            '1'
        )

        out = Template(
            "{% load wallets %}"
            "{% count_unpaid_symbol_invoices symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'ltc'
            })
        )

        self.assertEqual(
            out,
            '1'
        )

        out = Template(
            "{% load wallets %}"
            "{% count_unpaid_symbol_invoices symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'dash'
            })
        )

        self.assertEqual(
            out,
            '1'
        )

        out = Template(
            "{% load wallets %}"
            "{% count_unpaid_symbol_invoices symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'doge'
            })
        )

        self.assertEqual(
            out,
            '1'
        )

        out = Template(
            "{% load wallets %}"
            "{% count_unpaid_symbol_invoices symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'bcy'
            })
        )

        self.assertEqual(
            out,
            '1'
        )


class TestCountUnpaidSymbolPayments(TestCase):

    def setUp(self):
        self.user = self.make_user('user-{}'.format(random.randint(1, 100)))

    def test_without_invoices(self):
        request_factory = RequestFactory()
        request = request_factory.get('/')
        request.user = self.user

        out = Template(
            "{% load wallets %}"
            "{% count_unpaid_symbol_payments symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'btc'
            })
        )

        self.assertEqual(
            out,
            '0'
        )

        out = Template(
            "{% load wallets %}"
            "{% count_unpaid_symbol_payments symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'ltc'
            })
        )

        self.assertEqual(
            out,
            '0'
        )

        out = Template(
            "{% load wallets %}"
            "{% count_unpaid_symbol_payments symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'dash'
            })
        )

        self.assertEqual(
            out,
            '0'
        )

        out = Template(
            "{% load wallets %}"
            "{% count_unpaid_symbol_payments symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'doge'
            })
        )

        self.assertEqual(
            out,
            '0'
        )

        out = Template(
            "{% load wallets %}"
            "{% count_unpaid_symbol_payments symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'bcy'
            })
        )

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

        btc_invoice = factories.BtcInvoiceFactory(wallet=btc)
        ltc_invoice = factories.LtcInvoiceFactory(wallet=ltc)
        dash_invoice = factories.DashInvoiceFactory(wallet=dash)
        doge_invoice = factories.DogeInvoiceFactory(wallet=doge)
        bcy_invoice = factories.BcyInvoiceFactory(wallet=bcy)
        factories.PaymentBtcInvoiceFactory(
            invoice=btc_invoice,
            wallet=btc
        )
        factories.PaymentLtcInvoiceFactory(
            invoice=ltc_invoice,
            wallet=ltc
        )
        factories.PaymentDashInvoiceFactory(
            invoice=dash_invoice,
            wallet=dash
        )
        factories.PaymentDogeInvoiceFactory(
            invoice=doge_invoice,
            wallet=doge
        )
        factories.PaymentBcyInvoiceFactory(
            invoice=bcy_invoice,
            wallet=bcy
        )

        out = Template(
            "{% load wallets %}"
            "{% count_unpaid_symbol_payments symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'btc'
            })
        )

        self.assertEqual(
            out,
            '1'
        )

        out = Template(
            "{% load wallets %}"
            "{% count_unpaid_symbol_payments symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'ltc'
            })
        )

        self.assertEqual(
            out,
            '1'
        )

        out = Template(
            "{% load wallets %}"
            "{% count_unpaid_symbol_payments symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'dash'
            })
        )

        self.assertEqual(
            out,
            '1'
        )

        out = Template(
            "{% load wallets %}"
            "{% count_unpaid_symbol_payments symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'doge'
            })
        )

        self.assertEqual(
            out,
            '1'
        )

        out = Template(
            "{% load wallets %}"
            "{% count_unpaid_symbol_payments symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'bcy'
            })
        )

        self.assertEqual(
            out,
            '1'
        )


class TestCountUnpaidSymbol(TestCase):

    def setUp(self):
        self.user = self.make_user('user-{}'.format(random.randint(1, 100)))

    def test_without_invoices(self):
        request_factory = RequestFactory()
        request = request_factory.get('/')
        request.user = self.user

        out = Template(
            "{% load wallets %}"
            "{% count_unpaid_symbol symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'btc'
            })
        )

        self.assertEqual(
            out,
            '0'
        )

        out = Template(
            "{% load wallets %}"
            "{% count_unpaid_symbol symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'ltc'
            })
        )

        self.assertEqual(
            out,
            '0'
        )

        out = Template(
            "{% load wallets %}"
            "{% count_unpaid_symbol symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'dash'
            })
        )

        self.assertEqual(
            out,
            '0'
        )

        out = Template(
            "{% load wallets %}"
            "{% count_unpaid_symbol symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'doge'
            })
        )

        self.assertEqual(
            out,
            '0'
        )

        out = Template(
            "{% load wallets %}"
            "{% count_unpaid_symbol symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'bcy'
            })
        )

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

        btc_invoice = factories.BtcInvoiceFactory(wallet=btc)
        ltc_invoice = factories.LtcInvoiceFactory(wallet=ltc)
        dash_invoice = factories.DashInvoiceFactory(wallet=dash)
        doge_invoice = factories.DogeInvoiceFactory(wallet=doge)
        bcy_invoice = factories.BcyInvoiceFactory(wallet=bcy)
        factories.PaymentBtcInvoiceFactory(
            invoice=btc_invoice,
            wallet=btc
        )
        factories.PaymentLtcInvoiceFactory(
            invoice=ltc_invoice,
            wallet=ltc
        )
        factories.PaymentDashInvoiceFactory(
            invoice=dash_invoice,
            wallet=dash
        )
        factories.PaymentDogeInvoiceFactory(
            invoice=doge_invoice,
            wallet=doge
        )
        factories.PaymentBcyInvoiceFactory(
            invoice=bcy_invoice,
            wallet=bcy
        )

        out = Template(
            "{% load wallets %}"
            "{% count_unpaid_symbol symbol %}"
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
            "{% load wallets %}"
            "{% count_unpaid_symbol symbol %}"
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
            "{% load wallets %}"
            "{% count_unpaid_symbol symbol %}"
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
            "{% load wallets %}"
            "{% count_unpaid_symbol symbol %}"
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
            "{% load wallets %}"
            "{% count_unpaid_symbol symbol %}"
        ).render(Context({
            'request': request,
            'symbol': 'bcy'
        }
        ))

        self.assertEqual(
            out,
            '2'
        )
'''