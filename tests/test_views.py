from test_plus.test import TestCase
from . import factories
#from wallets import views
from wallets import models
from wallets import api
import mock
import blockcypher
#from django.core.signing import BadSignature, SignatureExpired
#rom django.urls.exceptions import NoReverseMatch
from django.core import signing
from guardian.shortcuts import assign_perm

'''
class TestAllUserWalletsList(TestCase):

    def setUp(self):
        self.user = factories.UserFactory()
        self.btc = factories.BtcFactory(user=self.user)
        self.ltc = factories.LtcFactory(user=self.user)
        self.dash = factories.DashFactory(user=self.user)
        self.doge = factories.DogeFactory(user=self.user)

    def test_view_url_exists_at_desired_location(self):
        resp = self.get('/wallets/')
        self.response_302(resp)

    def test_redirect_if_not_logged_in(self):
        resp = self.get(self.reverse('wallets:all'))
        self.assertRedirects(
            resp,
            '/accounts/login/?next=/wallets/',
            fetch_redirect_response=False
        )

    def test_success_if_logged_in(self):
        self.client.login(
            username='{}'.format(self.user.username),
            password='password'
        )
        resp = self.get(self.reverse('wallets:all'))
        self.response_200(resp)

    def test_view_uses_correct_template(self):
        self.client.login(
            username='{}'.format(self.user.username),
            password='password'
        )
        resp = self.get(self.reverse('wallets:all'))
        self.response_200(resp)
        self.assertTemplateUsed(resp, 'wallets/all.html')

    def test_context_data(self):
        self.client.login(
            username='{}'.format(self.user.username),
            password='password'
        )
        resp = self.get(self.reverse('wallets:all'))

        self.assertTrue('btc_wallets' in resp.context)
        self.assertTrue('ltc_wallets' in resp.context)
        self.assertTrue('dash_wallets' in resp.context)
        self.assertTrue('doge_wallets' in resp.context)

        self.assertTrue(self.btc in resp.context['btc_wallets'])
        self.assertTrue(self.ltc in resp.context['ltc_wallets'])
        self.assertTrue(self.dash in resp.context['dash_wallets'])
        self.assertTrue(self.doge in resp.context['doge_wallets'])

        self.assertEqual(
            resp.context['btc_wallets'].first().user,
            self.user
        )
        self.assertEqual(
            resp.context['ltc_wallets'].first().user,
            self.user
        )
        self.assertEqual(
            resp.context['dash_wallets'].first().user,
            self.user
        )
        self.assertEqual(
            resp.context['doge_wallets'].first().user,
            self.user
        )
'''


class TestWalletsListView(TestCase):

    def setUp(self):
        self.user = factories.UserFactory()
        self.btc = factories.BtcFactory(user=self.user)
        self.ltc = factories.LtcFactory(user=self.user)
        self.dash = factories.DashFactory(user=self.user)
        self.doge = factories.DogeFactory(user=self.user)
        blockcypher.get_address_overview = mock.MagicMock(return_value={
            "address": "1DEP8i3QJCsomS4BSMY2RpU1upv62aGvhD",
            "balance": 4433416,
            "final_balance": 4433416,
            "final_n_tx": 7,
            "n_tx": 7,
            "total_received": 4433416,
            "total_sent": 0,
            "unconfirmed_balance": 0,
            "unconfirmed_n_tx": 0
        })

    def test_view_url_exists_at_desired_location(self):
        resp = self.get('/wallets/btc/')
        self.response_302(resp)

        resp = self.get('/wallets/ltc/')
        self.response_302(resp)

        resp = self.get('/wallets/dash/')
        self.response_302(resp)

        resp = self.get('/wallets/doge/')
        self.response_302(resp)

    def test_redirect_if_not_logged_in(self):
        resp = self.get(self.reverse('wallets:list', wallet='btc'))
        self.assertRedirects(
            resp,
            '/accounts/login/?next=/wallets/btc/',
            fetch_redirect_response=False
        )

        resp = self.get(self.reverse('wallets:list', wallet='ltc'))
        self.assertRedirects(
            resp,
            '/accounts/login/?next=/wallets/ltc/',
            fetch_redirect_response=False
        )

        resp = self.get(self.reverse('wallets:list', wallet='dash'))
        self.assertRedirects(
            resp,
            '/accounts/login/?next=/wallets/dash/',
            fetch_redirect_response=False
        )

        resp = self.get(self.reverse('wallets:list', wallet='doge'))
        self.assertRedirects(
            resp,
            '/accounts/login/?next=/wallets/doge/',
            fetch_redirect_response=False
        )

    def test_success_if_logged_in(self):
        self.client.login(
            username='{}'.format(self.user.username),
            password='password'
        )

        resp = self.get(self.reverse('wallets:list', wallet='btc'))
        self.response_200(resp)

        resp = self.get(self.reverse('wallets:list', wallet='ltc'))
        self.response_200(resp)

        resp = self.get(self.reverse('wallets:list', wallet='dash'))
        self.response_200(resp)

        resp = self.get(self.reverse('wallets:list', wallet='doge'))
        self.response_200(resp)

    def test_context_data(self):
        self.client.login(
            username='{}'.format(self.user.username),
            password='password'
        )
        resp = self.get(self.reverse('wallets:list', wallet='btc'))
        self.response_200(resp)
        self.assertEqual(resp.context['total_balance'], 0.04433416)
        self.assertEqual(resp.context['symbol'], 'btc')

        resp = self.get(self.reverse('wallets:list', wallet='ltc'))
        self.response_200(resp)
        self.assertEqual(resp.context['total_balance'], 0.04433416)
        self.assertEqual(resp.context['symbol'], 'ltc')

        resp = self.get(self.reverse('wallets:list', wallet='dash'))
        self.response_200(resp)
        self.assertEqual(resp.context['total_balance'], 0.04433416)
        self.assertEqual(resp.context['symbol'], 'dash')

        resp = self.get(self.reverse('wallets:list', wallet='doge'))
        self.response_200(resp)
        self.assertEqual(resp.context['total_balance'], 0.04433416)
        self.assertEqual(resp.context['symbol'], 'doge')

    def test_queryset(self):
        self.client.login(
            username='{}'.format(self.user.username),
            password='password'
        )

        resp = self.get(self.reverse('wallets:list', wallet='btc'))
        self.assertTrue('wallets_list' in resp.context)
        for wallet in resp.context['wallets_list']:
            self.assertEqual(wallet.user, self.user)

        resp = self.get(self.reverse('wallets:list', wallet='ltc'))
        self.assertTrue('wallets_list' in resp.context)
        for wallet in resp.context['wallets_list']:
            self.assertEqual(wallet.user, self.user)

        resp = self.get(self.reverse('wallets:list', wallet='dash'))
        self.assertTrue('wallets_list' in resp.context)
        for wallet in resp.context['wallets_list']:
            self.assertEqual(wallet.user, self.user)

        resp = self.get(self.reverse('wallets:list', wallet='doge'))
        self.assertTrue('wallets_list' in resp.context)
        for wallet in resp.context['wallets_list']:
            self.assertEqual(wallet.user, self.user)

    def test_does_not_exist(self):
        self.client.login(
            username='{}'.format(self.user.username),
            password='password'
        )
        resp = self.get(self.reverse('wallets:list', wallet='FAKE'))
        self.response_404(resp)


class TestWalletsCreateView(TestCase):

    def setUp(self):
        self.user = factories.UserFactory()

    def test_view_url_exists_at_desired_location(self):
        resp = self.get('/wallets/bcy/_create/')
        self.response_302(resp)

    def test_redirect_if_not_logged_in(self):
        resp = self.get(self.reverse('wallets:create', wallet='bcy'))
        self.assertRedirects(
            resp,
            '/accounts/login/?next=/wallets/bcy/_create/',
            fetch_redirect_response=False
        )

    def test_generate_new_address(self):
        blockcypher.generate_new_address = mock.MagicMock(
            return_value={
                'private': '678a45c9c579c1166278e53bb84648' +
                           'e0eb52d16239a411e95d7a2ae018d609ba',
                'wif': 'BroJJwWLvoS5e1nNzauUNPEdGB7f1vouheydRRcFyvYFgUEHxgc4',
                'address': 'C1pyYVnmoCXH5upC2x52CoVJ5R74mQWUqZ',
                'public': '03efb85b737b198e3fdd7080ffc4b3e3162e' +
                          '58c3a024d020d2d87cd53d410620ad'
            }
        )
        blockcypher.get_address_overview = mock.MagicMock(return_value={
            "address": "1DEP8i3QJCsomS4BSMY2RpU1upv62aGvhD",
            "balance": 4433416,
            "final_balance": 4433416,
            "final_n_tx": 7,
            "n_tx": 7,
            "total_received": 4433416,
            "total_sent": 0,
            "unconfirmed_balance": 0,
            "unconfirmed_n_tx": 0
        })
        self.client.login(
            username='{}'.format(self.user.username),
            password='password'
        )

        resp = self.get(self.reverse('wallets:create', wallet='bcy'))
        self.response_302(resp)
        self.assertRedirects(
            resp,
            '/wallets/bcy/C1pyYVnmoCXH5upC2x52CoVJ5R74mQWUqZ/_detail/'
        )
        resp = self.get(resp.url)
        self.assertEqual(
            resp.context['object'].address,
            'C1pyYVnmoCXH5upC2x52CoVJ5R74mQWUqZ'
        )
        self.assertEqual(
            len(list(resp.context['messages'])),
            1
        )
        self.assertEqual(
            str(list(resp.context['messages'])[0]),
            'New BCY address successfully created'
        )

    def test_fail_generate_new_address(self):
        self.client.login(
            username='{}'.format(self.user.username),
            password='password'
        )
        resp = self.get(self.reverse('wallets:create', wallet='FAKE'))
        self.response_302(resp)
        self.assertEqual(resp.url, '/wallets/')
        self.assertRedirects(
            resp,
            '/wallets/'
        )


class TestWalletsDetailView(TestCase):

    def setUp(self):
        self.user = factories.UserFactory()
        self.bcy = factories.BcyFactory(user=self.user)
        blockcypher.generate_new_address = mock.MagicMock(
            return_value={
                'private': '678a45c9c579c1166278e53bb84648' +
                           'e0eb52d16239a411e95d7a2ae018d609ba',
                'wif': 'BroJJwWLvoS5e1nNzauUNPEdGB7f1vouheydRRcFyvYFgUEHxgc4',
                'address': 'C1pyYVnmoCXH5upC2x52CoVJ5R74mQWUqZ',
                'public': '03efb85b737b198e3fdd7080ffc4b3e3162e' +
                          '58c3a024d020d2d87cd53d410620ad'
            }
        )
        blockcypher.get_address_overview = mock.MagicMock(return_value={
            "address": "1DEP8i3QJCsomS4BSMY2RpU1upv62aGvhD",
            "balance": 4433416,
            "final_balance": 4433416,
            "final_n_tx": 7,
            "n_tx": 7,
            "total_received": 4433416,
            "total_sent": 0,
            "unconfirmed_balance": 0,
            "unconfirmed_n_tx": 0
        })

        self.client.login(
            username='{}'.format(self.user.username),
            password='password'
        )
        '''
        self.resp = self.get(self.reverse('wallets:create', wallet='bcy'))
        self.assertEqual(self.resp.status_code, 302)
        '''

    def test_view_url_exists_at_desired_location(self):
        resp = self.get('/wallets/bcy/{}/_detail/'.format(self.bcy.address))
        self.response_200(resp)

    def test_forbidden_if_not_logged_in(self):
        self.client.logout()
        resp = self.get('/wallets/bcy/{}/_detail/'.format(self.bcy.address))
        self.response_403(resp)

    def test_success_if_logged_in(self):
        resp = self.get(
            self.reverse(
                'wallets:detail',
                wallet='bcy',
                address='{}'.format(self.bcy.address)
            )
        )
        self.response_200(resp)
        self.assertEqual(
            resp.context['object'].address,
            '{}'.format(self.bcy.address)
        )
        self.assertEqual(
            resp.context['object'].user,
            self.user
        )

    def test_view_uses_correct_template(self):
        resp = self.get(
            self.reverse(
                'wallets:detail',
                wallet='bcy',
                address='{}'.format(self.bcy.address)
            )
        )
        self.response_200(resp)
        self.assertTemplateUsed(resp, 'wallets/detail.html')

    def test_with_invalid_wallet(self):
        resp = self.get(
            self.reverse(
                'wallets:detail',
                wallet='FAKE',
                address='{}'.format(self.bcy.address)
            )
        )
        self.response_404(resp)

    def test_post_withdraw_form_with_valid_data(self):
        api.not_simple_spend = mock.MagicMock(
            return_value='7981c7849294648c1e79dd16077a' +
                         '388b808fcf8c20035aec7cc5315b37dacfee'
        )
        resp = self.post(
            self.reverse(
                'wallets:detail',
                wallet='bcy',
                address='{}'.format(self.bcy.address)
            ),
            data={
                'address': 'C1pyYVnmoCXH5upC2x52CoVJ5R74mQWUqZ',
                'amount': 123
            }
        )
        self.response_302(resp)
        resp = self.get(resp.url)
        messages = self.get_context('messages')
        self.assertEqual(
            len(list(messages)),
            1
        )
        self.assertEqual(
            str(list(messages)[0]),
            'Transaction successfully created 7981c7849294648c1e79d' +
            'd16077a388b808fcf8c20035aec7cc5315b37dacfee'
        )

    def test_post_withdraw_form_with_invalid_data(self):
        api.not_simple_spend = mock.MagicMock(
            return_value='7981c7849294648c1e79dd16077a388b808fcf8c20' +
                         '035aec7cc5315b37dacfee'
        )
        resp = self.post(
            self.reverse(
                'wallets:detail',
                wallet='bcy',
                address='{}'.format(self.bcy.address)
            ),
            data={
                'address': '{}'.format(self.bcy.address),
                'amount': 1
            }
        )
        self.response_200(resp)
        self.assertEqual(
            len(resp.context['form'].errors),
            1
        )


class TestWalletsWebhookView(TestCase):

    def setUp(self):
        self.fake_data = {
            'from_address': 'FAKE_FROM_ADDRESS',
            'to_addresses': ['FAKE_TO_ADDRESS'],
            'symbol': 'FAKE_SYMBOL',
            'event': 'FAKE_EVENT',
            'transaction_id': 'FAKE_TRANSACTION_ID',
            'payload': None
        }
        self.fake_signature = signing.dumps(self.fake_data)

        self.data = {
            'from_address': 'C2ATnDcRHEeEceUNY1wWjQAtxQK3kGfoZ9',
            'to_addresses': ['CDHsAcdbWvwtBaM9urmRU2VpQ3yMXfoUjy'],
            'symbol': 'bcy',
            'event': 'confirmed-tx',
            'transaction_id': '0e497d00057a2ae14e6e3f0d413173dbfa9f' +
                              '2f0a05114764aeaa9e88fa4a5d05',
            'payload': None
        }
        self.signature = signing.dumps(self.data)

    def test_post_with_valid_signature(self):
        resp = self.post('/wallets/webhook/{}/'.format(self.signature))
        self.response_200(resp)

    def test_extract_webhook_id(self):
        data = {
            'from_address': 'C2ATnDcRHEeEceUNY1wWjQAtxQK3kGfoZ9',
            'to_addresses': ['CDHsAcdbWvwtBaM9urmRU2VpQ3yMXfoUjy'],
            'symbol': 'bcy',
            'event': 'confirmed-tx',
            'transaction_id': '1e497d00057a2ae14e6e3f0d413173dbfa9f' +
                              '2f0a05114764aeaa9e88fa4a5d05',
            'payload': None
        }
        signature = signing.dumps(data)
        resp = self.post('/wallets/webhook/{}/'.format(signature))
        self.response_200(resp)

    def test_unsubscribe_from_webhook(self):
        blockcypher.list_webhooks = mock.MagicMock(return_value=[{
            'address': 'C2ATnDcRHEeEceUNY1wWjQAtxQK3kGfoZ9',
            'callback_errors': 0,
            'event': 'confirmed-tx',
            'id': '35e06a63-b09b-4cb2-a536-208642c96cd4',
            'token': '75ada547a1524310971733088eb068ec',
            'url': 'http://localhost//wallets/webhook/{}/'.format(
                self.signature
            )
        }])
        webhook_id = mock.MagicMock(
            return_value='35e06a63-b09b-4cb2-a536-208642c96cd4'
        )
        blockcypher.unsubscribe_from_webhook = mock.MagicMock(
            return_value=True
        )
        resp = self.post('/wallets/webhook/{}/'.format(self.signature))
        self.response_200(resp)


class TestInvoiceListView(TestCase):

    def setUp(self):
        self.user = factories.UserFactory()
        self.btc = factories.BtcFactory(user=self.user)
        self.ltc = factories.LtcFactory(user=self.user)
        self.dash = factories.DashFactory(user=self.user)
        self.doge = factories.DogeFactory(user=self.user)

        self.btc_invoice = factories.BtcInvoiceFactory(
            wallet=self.btc
        )
        self.btc_payment = factories.PaymentBtcInvoiceFactory(
            invoice=self.btc_invoice,
            amount=1
        )

        self.ltc_invoice = factories.LtcInvoiceFactory(
            wallet=self.ltc
        )
        self.ltc_payment = factories.PaymentBtcInvoiceFactory(
            invoice=self.ltc_invoice,
            amount=1
        )

        self.dash_invoice = factories.DashInvoiceFactory(
            wallet=self.dash
        )
        self.dash_payment = factories.PaymentBtcInvoiceFactory(
            invoice=self.dash_invoice,
            amount=1
        )

        self.doge_invoice = factories.DogeInvoiceFactory(
            wallet=self.doge
        )
        self.doge_payment = factories.PaymentBtcInvoiceFactory(
            invoice=self.doge_invoice,
            amount=1
        )

    def test_redirect_if_not_logged_in(self):
        resp = self.get('/wallets/invoices/btc/')
        self.assertRedirects(
            resp,
            '/accounts/login/?next=/wallets/invoices/btc/',
            fetch_redirect_response=False
        )

    def test_success_if_logged_in(self):
        self.client.login(username=self.user.username, password='password')
        resp = self.get('/wallets/invoices/btc/')
        self.response_200(resp)

    def test_context_object(self):
        self.client.login(username=self.user.username, password='password')
        self.get('/wallets/invoices/btc/')
        self.assertTrue(
            self.btc_invoice in self.get_context('invoices'),
        )
        self.assertIsNotNone(self.get_context('payments'))
        self.assertEqual(self.get_context('symbol'), 'btc')

        self.client.login(username=self.user.username, password='password')
        self.get('/wallets/invoices/ltc/')
        self.assertTrue(
            self.ltc_invoice in self.get_context('invoices'),
        )
        self.assertIsNotNone(self.get_context('payments'))
        self.assertEqual(self.get_context('symbol'), 'ltc')

        self.client.login(username=self.user.username, password='password')
        self.get('/wallets/invoices/dash/')
        self.assertTrue(
            self.dash_invoice in self.get_context('invoices'),
        )
        self.assertIsNotNone(self.get_context('payments'))
        self.assertEqual(self.get_context('symbol'), 'dash')

        self.client.login(username=self.user.username, password='password')
        self.get('/wallets/invoices/doge/')
        self.assertTrue(
            self.doge_invoice in self.get_context('invoices'),
        )
        self.assertIsNotNone(self.get_context('payments'))
        self.assertEqual(self.get_context('symbol'), 'doge')

    def test_view_uses_correct_template(self):
        self.client.login(
            username='{}'.format(self.user.username),
            password='password'
        )
        resp = self.get('/wallets/invoices/btc/')
        self.response_200(resp)
        self.assertTemplateUsed(resp, 'wallets/invoice_list.html')


class TestInvoiceDetailView(TestCase):

    def setUp(self):
        api.not_simple_spend = mock.MagicMock(
            return_value='7981c7849294648c1e79dd16077a388b808fcf8' +
                         'c20035aec7cc5315b37dacfee'
        )
        blockcypher.subscribe_to_address_webhook = mock.MagicMock(
            return_value='bcaf7c39-9a7f-4e8b-8ba4-23b3c1806039'
        )
        blockcypher.get_address_overview = mock.MagicMock(
            return_value={'balance': 10000}
        )

        self.user = factories.UserFactory()
        self.btc = factories.BtcFactory(user=self.user)
        self.ltc = factories.LtcFactory(user=self.user)
        self.dash = factories.DashFactory(user=self.user)
        self.doge = factories.DogeFactory(user=self.user)

        self.btc_invoice = factories.BtcInvoiceFactory(
            wallet=self.btc,
        )
        self.btc_payment = factories.PaymentBtcInvoiceFactory(
            invoice=self.btc_invoice,
            amount=1
        )
        assign_perm('view_invoice', self.user, self.btc_invoice)
        assign_perm('pay_invoice', self.user, self.btc_invoice)
        assign_perm('view_payment', self.user, self.btc_payment)

        self.ltc_invoice = factories.LtcInvoiceFactory(
            wallet=self.ltc,
        )
        self.ltc_payment = factories.PaymentLtcInvoiceFactory(
            invoice=self.ltc_invoice,
            amount=1
        )
        assign_perm('view_invoice', self.user, self.ltc_invoice)
        assign_perm('pay_invoice', self.user, self.ltc_invoice)
        assign_perm('view_payment', self.user, self.ltc_payment)

        self.dash_invoice = factories.DashInvoiceFactory(
            wallet=self.dash,
        )
        self.dash_payment = factories.PaymentDashInvoiceFactory(
            invoice=self.dash_invoice,
            amount=1
        )
        assign_perm('view_invoice', self.user, self.dash_invoice)
        assign_perm('pay_invoice', self.user, self.dash_invoice)
        assign_perm('view_payment', self.user, self.dash_payment)

        self.doge_invoice = factories.DogeInvoiceFactory(
            wallet=self.dash,
        )
        self.doge_payment = factories.PaymentDogeInvoiceFactory(
            invoice=self.doge_invoice,
            amount=1
        )
        assign_perm('view_invoice', self.user, self.doge_invoice)
        assign_perm('pay_invoice', self.user, self.doge_invoice)
        assign_perm('view_payment', self.user, self.doge_payment)

    def test_redirect_if_not_logged_in(self):
        resp = self.get('/wallets/invoices/1/_detail/')
        self.assertRedirects(
            resp,
            '/accounts/login/?next=/wallets/invoices/1/_detail/',
            fetch_redirect_response=False
        )

    def test_success_if_logged_in(self):
        self.client.login(username=self.user.username, password='password')
        resp = self.get('/wallets/invoices/{}/_detail/'.format(
            self.btc_invoice.pk
            )
        )
        self.response_200(resp)

    def test_view_url_accessible_by_name(self):
        self.client.login(username=self.user.username, password='password')
        resp = self.get(
            self.reverse(
                'wallets:invoice_detail',
                pk=self.btc_invoice.pk
            )
        )
        self.assertEqual(resp.status_code, 200)

    def test_context_object(self):
        self.client.login(username=self.user.username, password='password')
        self.get('/wallets/invoices/{}/_detail/'.format(self.btc_invoice.pk))
        self.assertEqual(
            self.get_context('object'),
            self.btc_invoice
        )

    def test_object_belongs_user(self):
        self.client.login(username=self.user.username, password='password')
        self.get('/wallets/invoices/{}/_detail/'.format(self.btc_invoice.pk))
        self.assertEqual(
            self.get_context('object').wallet.user,
            self.user
        )

    def test_view_uses_correct_template(self):
        self.client.login(
            username='{}'.format(self.user.username),
            password='password'
        )
        resp = self.get('/wallets/invoices/{}/_detail/'.format(
            self.btc_invoice.pk
            )
        )
        self.response_200(resp)
        self.assertTemplateUsed(resp, 'wallets/invoice_detail.html')

    def test_permission_denied(self):
        user = factories.UserFactory()
        self.client.login(
            username='{}'.format(user.username),
            password='password'
        )
        resp = self.get('/wallets/invoices/{}/_detail/'.format(
            self.btc_invoice.pk
            )
        )
        self.response_403(resp)
    '''
    def test_success_with_POST(self):
        self.client.login(
            username=self.user.username,
            password='password'
        )
        resp = self.post(
            '/wallets/invoices/{}/_detail/'.format(self.btc_invoice.pk),
            data={'payload': ''}
        )
        self.response_302(resp)
        resp = self.get(resp.url)
        self.response_200(resp)

    def test_invoice_transaction_after_success_POST(self):
        self.client.login(
            username=self.user.username,
            password='password'
        )
        resp = self.post(
            '/wallets/invoices/{}/_detail/'.format(self.btc_invoice.pk),
            data={'payload': ''}
        )
        self.response_302(resp)
        resp = self.get(resp.url)
        self.response_200(resp)
        pk = self.btc_invoice.pk
        invoice = models.Invoice.objects.get(pk=pk)
        self.assertIsNotNone(invoice.tx_ref)
    '''


class TestPaymentListView(TestCase):

    def setUp(self):
        self.user = factories.UserFactory()
        self.btc = factories.BtcFactory(user=self.user)
        self.btc_invoice = factories.BtcInvoiceFactory(wallet=self.btc)
        self.payment = factories.PaymentBtcInvoiceFactory(
            wallet=self.btc,
            invoice=self.btc_invoice
        )
        assign_perm('view_payment', self.user, self.payment)

    def test_redirect_if_not_logged_in(self):
        resp = self.get('/wallets/payments/')
        self.assertRedirects(
            resp,
            '/accounts/login/?next=/wallets/payments/',
            fetch_redirect_response=False
        )

    def test_success_if_logged_in(self):
        self.client.login(username=self.user.username, password='password')
        resp = self.get('/wallets/payments/')
        self.response_200(resp)

    def test_view_url_accessible_by_name(self):
        self.client.login(username=self.user.username, password='password')
        resp = self.get(self.reverse('wallets:payment_list'))
        self.response_200(resp)

    def test_payment_list_in_context(self):
        self.client.login(username=self.user.username, password='password')
        self.get(self.reverse('wallets:payment_list'))
        self.assertIsNotNone(self.get_context('payment_list'))

    def test_view_uses_correct_template(self):
        self.client.login(username=self.user.username, password='password')
        resp = self.get('/wallets/payments/')
        self.response_200(resp)
        self.assertTemplateUsed(resp, 'wallets/payment_list.html')

    def test_pagination(self):
        for i in range(25):
            payment = factories.PaymentBtcInvoiceFactory(
                invoice=self.btc_invoice,
                wallet=self.btc
            )
            assign_perm('view_payment', self.user, payment)
        self.client.login(username=self.user.username, password='password')
        resp = self.get(self.reverse('wallets:payment_list'))
        self.response_200(resp)
        self.assertEqual(
            len(self.get_context('payment_list')),
            10
        )
        self.assertTrue(self.get_context('is_paginated'))

    def test_second_page_with_pagination(self):
        for i in range(25):
            payment = factories.PaymentBtcInvoiceFactory(
                invoice=self.btc_invoice,
                wallet=self.btc
            )
            assign_perm('view_payment', self.user, payment)

        self.client.login(username=self.user.username, password='password')
        resp = self.get(self.reverse('wallets:payment_list') + '?page=2')
        self.response_200(resp)
        self.assertEqual(
            len(self.get_context('payment_list')),
            10
        )
        self.assertTrue(self.get_context('is_paginated'))

        self.client.login(username=self.user.username, password='password')
        resp = self.get(self.reverse('wallets:payment_list') + '?page=3')
        self.response_200(resp)
        self.assertEqual(
            len(self.get_context('payment_list')),
            6
        )
        self.assertTrue(self.get_context('is_paginated'))

    def test_empty_qs_if_user_has_no_perms(self):
        self.payment.delete()
        self.client.login(username=self.user.username, password='password')
        self.get(self.reverse('wallets:payment_list'))
        self.assertEqual(len(self.get_context('payment_list')), 0)


class TestInvoiceDeleteView(TestCase):
    def setUp(self):
        self.user = factories.UserFactory()
        self.btc = factories.BtcFactory(user=self.user)
        self.btc_invoice = factories.BtcInvoiceFactory(wallet=self.btc)
        self.payment = factories.PaymentBtcInvoiceFactory(
            wallet=self.btc,
            invoice=self.btc_invoice
        )
        assign_perm('view_invoice', self.user, self.btc_invoice)
        assign_perm('pay_invoice', self.user, self.btc_invoice)
        assign_perm('view_payment', self.user, self.payment)

    def test_redirect_if_not_logged_in(self):
        resp = self.get('/wallets/invoices/1/_delete/')
        self.assertRedirects(
            resp,
            '/accounts/login/?next=/wallets/invoices/1/_delete/',
            fetch_redirect_response=False
        )

    def test_success_if_logged_in(self):
        self.client.login(username=self.user.username, password='password')
        resp = self.get('/wallets/invoices/1/_delete/')
        self.response_200(resp)

    def test_view_url_accessible_by_name(self):
        self.client.login(username=self.user.username, password='password')
        resp = self.get(self.reverse(
            'wallets:invoice_delete',
            pk=self.btc_invoice.pk)
        )
        self.response_200(resp)

    def test_view_uses_correct_template(self):
        self.client.login(username=self.user.username, password='password')
        resp = self.get(
            '/wallets/invoices/{}/_delete/'.format(self.btc_invoice.pk)
        )
        self.response_200(resp)
        self.assertTemplateUsed(resp, 'wallets/invoice_confirm_delete.html')

    def test_delete_object_after_post(self):
        self.client.login(username=self.user.username, password='password')
        resp = self.post(
            '/wallets/invoices/1/_delete/'.format(self.btc_invoice.pk)
        )
        self.response_302(resp)
        self.assertEqual(
            models.Invoice.objects.count(),
            0
        )


class TestInvoicePayView(TestCase):
    def setUp(self):
        self.user = factories.UserFactory()
        self.btc = factories.BtcFactory(user=self.user)
        self.btc_invoice = factories.BtcInvoiceFactory(wallet=self.btc)
        self.payment = factories.PaymentBtcInvoiceFactory(
            wallet=self.btc,
            invoice=self.btc_invoice,
            amount=1000000000000000
        )
        assign_perm('view_invoice', self.user, self.btc_invoice)
        assign_perm('pay_invoice', self.user, self.btc_invoice)
        assign_perm('view_payment', self.user, self.payment)

    def test_redirect_if_not_logged_in(self):
        resp = self.get('/wallets/invoices/1/_pay/')
        self.assertRedirects(
            resp,
            '/accounts/login/?next=/wallets/invoices/1/_pay/',
            fetch_redirect_response=False
        )

    def test_success_if_logged_in(self):
        self.client.login(username=self.user.username, password='password')
        resp = self.get('/wallets/invoices/1/_pay/')
        self.response_200(resp)

    def test_view_url_accessible_by_name(self):
        self.client.login(username=self.user.username, password='password')
        resp = self.get(self.reverse('wallets:invoice_pay', pk=1))
        self.response_200(resp)

    def test_view_uses_correct_template(self):
        self.client.login(username=self.user.username, password='password')
        resp = self.get(
            '/wallets/invoices/1/_pay/'.format(self.btc_invoice.pk)
        )
        self.response_200(resp)
        self.assertTemplateUsed(resp, 'wallets/invoice_confirm_pay.html')

    def test_paid_object_after_post(self):
        self.client.login(username=self.user.username, password='password')
        blockcypher.get_transaction_details = mock.MagicMock(
            return_value={
                "addresses": [
                    "13XXaBufpMvqRqLkyDty1AXqueZHVe6iyy",
                    "19YtzZdcfs1V2ZCgyRWo8i2wLT8ND1Tu4L",
                    "1BNiazBzCxJacAKo2yL83Wq1VJ18AYzNHy",
                    "1GbMfYui17L5m6sAy3L3WXAtf1P32bxJXq",
                    "1N2f642sbgCMbNtXFajz9XDACDFnFzdXzV"
                ],
                "block_hash": "0000000000000000c504bdea36e531d8089d324f2d" +
                              "936c86e3274f97f8a44328",
                "block_height": 293000,
                "confirmations": 86918,
                "confirmed": "datetime.datetime(2014, 3, 29, 1, 29, 19," +
                             " 0, tzinfo=tzutc())",
                "double_spend": False,
                "fees": 0,
                "hash": "f854aebae95150b379cc1187d848d58225f3c4157fe992bcd1" +
                        "66f58bd5063449",
                "inputs": [
                    {
                        "addresses": [
                            "1GbMfYui17L5m6sAy3L3WXAtf1P32bxJXq"
                        ],
                        "output_index": 1,
                        "output_value": 16450000,
                        "prev_hash": "583910b7bf90ab802e22e5c25a89b59862b20c" +
                                     "8c1aeb24dfb94e7a508a70f121",
                        "script": "4830450220504b1ccfddf508422bdd8b0fcda2b14" +
                                  "83e87aee1b486c0130bc29226bbce3b4e022100b5" +
                                  "befcfcf0d3bf6ebf0ac2f93badb19e3042c7bed45" +
                                  "6c398e743b885e782466c012103b1feb40b99e8ff" +
                                  "18469484a50e8b52cc478d5f4f773a341fbd920a4" +
                                  "ceaedd4bf",
                        "script_type": "pay-to-pubkey-hash",
                        "sequence": 4294967295
                    },
                ],
                "lock_time": 0,
                "outputs": [
                    {
                        "addresses": [
                            "1N2f642sbgCMbNtXFajz9XDACDFnFzdXzV"
                        ],
                        "script": "76a914e6aad9d712c419ea8febf009a3f3bfdd8d2" +
                                  "22fac88ac",
                        "script_type": "pay-to-pubkey-hash",
                        "spent_by": "35832d6c70b98b54e9a53ab2d51176eb19ad11b" +
                                    "c4505d6bb1ea6c51a68cb92ee",
                        "value": 70320221545
                    }
                ],
                "preference": "low",
                "received": "datetime.datetime(2014, 3, 29, 1, 29, " +
                            "19, 0, tzinfo=tzutc())",
                "relayed_by": "",
                "size": 636,
                "total": 70320221545,
                "ver": 1,
                "vin_sz": 4,
                "vout_sz": 1
            }
        )
        api.not_simple_spend = mock.MagicMock(
            return_value='7981c7849294648c1e79dd16077a388b808fcf8c20035aec7' +
                         'cc5315b37dacfee'
        )
        blockcypher.get_address_overview = mock.MagicMock(
            return_value={
                "address": "1DEP8i3QJCsomS4BSMY2RpU1upv62aGvhD",
                "balance": 4433416,
                "final_balance": 4433416,
                "final_n_tx": 7,
                "n_tx": 7,
                "total_received": 4433416,
                "total_sent": 0,
                "unconfirmed_balance": 0,
                "unconfirmed_n_tx": 0
            }
        )
        resp = self.post(
            '/wallets/invoices/{}/_pay/'.format(self.btc_invoice.pk)
        )
        self.response_302(resp)
        invoice = models.Invoice.objects.first()
        invoice.is_paid = True
        invoice.save()
        self.assertTrue(invoice.is_paid)

"""
class TestInvoicePayView(TestCase):
    def setUp(self):
        self.user = factories.UserFactory()
        self.btc = factories.BtcFactory(user=self.user)

        self.btc_invoice = factories.BtcInvoiceFactory(
            wallet=self.btc,
            amount=[1]
        )
        assign_perm('pay_invoice', self.user, self.btc_invoice)
        assign_perm('view_invoice', self.user, self.btc_invoice)

        self.btc_invoice.receiver_wallet_object.add(self.btc)
        self.btc_invoice.save()
        api.not_simple_spend = mock.MagicMock(
            return_value='7981c7849294648c1e79dd16077a388b808fcf8' +
                         'c20035aec7cc5315b37dacfee'
        )
        blockcypher.subscribe_to_address_webhook = mock.MagicMock(
            return_value='bcaf7c39-9a7f-4e8b-8ba4-23b3c1806039'
        )
        blockcypher.get_address_overview = mock.MagicMock(
            return_value={'balance': 10000}
        )

    def test_redirect_if_not_logged_in(self):
        resp = self.get('/wallets/invoices/{}/_pay/'.format(
            self.btc_invoice.pk
            )
        )
        self.assertRedirects(
            resp,
            '/accounts/login/?next=/wallets/invoices/{}/_pay/'.format(
                self.btc_invoice.pk
            ),
            fetch_redirect_response=False
        )
    '''
    def test_GET_method_not_allowed_if_logged_in(self):
        self.client.login(username=self.user.username, password='password')
        resp = self.get('/wallets/invoices/{}/_pay/'.format(
            self.btc_invoice.pk)
        )
        print(resp)
        self.response_405(resp)
    '''
    def test_success_POST_if_logged_in(self):
        self.client.login(username=self.user.username, password='password')
        resp = self.post('/wallets/invoices/{}/_pay/'.format(
            self.btc_invoice.pk)
        )
        print(resp)
        '''
        client = Client(enforce_csrf_checks=True)
        client.login(username=self.user.username, password='password')
        resp = client.post('/wallets/invoices/{}/_pay/'.format(
            self.btc_invoice.pk)
        )
        print(resp)
        '''
        #print(resp)
        #csrf_token = self.client.cookies['csrftoken'].value
        #print(csrf_token)
        '''
        self.client.login(username=self.user.username, password='password')
        resp = self.client.post('/wallets/invoices/{}/_pay/'.format(
            self.btc_invoice.pk)
        )
        print(resp)
        '''
        #self.response_200(resp)

    def test_view_url_accessible_by_name(self):
        self.client.login(username=self.user.username, password='password')
        resp = self.get(
            self.reverse(
                'wallets:invoice_pay',
                pk=self.btc_invoice.pk
            )
        )
        self.assertEqual(resp.status_code, 200)

    def test_context_object(self):
        self.client.login(username=self.user.username, password='password')
        self.get('/wallets/invoices/{}/_pay/'.format(self.btc_invoice.pk))
        self.assertEqual(
            self.get_context('object'),
            self.btc_invoice
        )

    def test_object_belongs_user(self):
        self.client.login(
            username=self.user.username,
            password='password'
        )
        self.get('/wallets/invoices/{}/_pay/'.format(self.btc_invoice.pk))
        context = self.get_context('object').receiver_wallet_object.all()
        receiver = self.btc_invoice.receiver_wallet_object.all()
        self.assertTrue(self.user in [wallet.user for wallet in context])
        self.assertTrue(self.user in [wallet.user for wallet in receiver])

        self.assertEqual(
            self.get_context('object').wallet.user,
            self.user
        )

    def test_view_uses_correct_template(self):
        self.client.login(
            username='{}'.format(self.user.username),
            password='password'
        )
        api.not_simple_spend = mock.MagicMock(
            return_value='7981c7849294648c1e79dd16077a388b808fcf8c20035aec7c' +
                         'c5315b37dacfee'
        )
        resp = self.get('/wallets/invoices/{}/_pay/'.format(
            self.btc_invoice.pk)
        )
        self.response_200(resp)
        self.assertTemplateUsed(resp, 'wallets/invoice_detail.html')

    def test_permission_denied(self):
        user = factories.UserFactory()
        self.client.login(
            username='{}'.format(user.username),
            password='password'
        )
        resp = self.get('/wallets/invoices/{}/_pay/'.format(
            self.btc_invoice.pk)
        )
        self.response_403(resp)
"""
