from test_plus.test import TestCase
from . import factories
from wallets import views 
from wallets import models
from wallets import api
import mock
import blockcypher 
from django.core.signing import BadSignature, SignatureExpired
from django.urls.exceptions import NoReverseMatch
from django.core import signing


class TestAllUserWalletsList(TestCase):

	def setUp(self):
		self.user = factories.UserFactory()
		self.btc = factories.BtcFactory(user = self.user)
		self.ltc = factories.LtcFactory(user = self.user)
		self.dash = factories.DashFactory(user = self.user)
		self.doge = factories.DogeFactory(user = self.user)

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
		login = self.client.login(
			username='{}'.format(self.user.username),
			password='password'
		)
		resp = self.get(self.reverse('wallets:all'))
		self.response_200(resp)

	def test_view_uses_correct_template(self):
		login = self.client.login(
			username='{}'.format(self.user.username),
			password='password'
		)
		resp = self.get(self.reverse('wallets:all'))
		self.response_200(resp)
		self.assertTemplateUsed(resp, 'wallets/all.html')

	def test_context_data(self):
		login = self.client.login(
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


class TestWalletsListView(TestCase):

	def setUp(self):
		self.user = factories.UserFactory()
		self.btc = factories.BtcFactory(user = self.user)
		self.ltc = factories.LtcFactory(user = self.user)
		self.dash = factories.DashFactory(user = self.user)
		self.doge = factories.DogeFactory(user = self.user)
		blockcypher.get_address_overview = mock.MagicMock(return_value=
			{
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
		login = self.client.login(
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
		login = self.client.login(
			username='{}'.format(self.user.username),
			password='password'
		)
		resp = self.get(self.reverse('wallets:list', wallet='btc'))
		self.response_200(resp)
		self.assertEqual(resp.context['total_balance'], 4433416)
		self.assertEqual(resp.context['symbol'], 'btc')

		
		resp = self.get(self.reverse('wallets:list', wallet='ltc'))
		self.response_200(resp)
		self.assertEqual(resp.context['total_balance'], 4433416)
		self.assertEqual(resp.context['symbol'], 'ltc')

		resp = self.get(self.reverse('wallets:list', wallet='dash'))
		self.response_200(resp)
		self.assertEqual(resp.context['total_balance'], 4433416)
		self.assertEqual(resp.context['symbol'], 'dash')

		resp = self.get(self.reverse('wallets:list', wallet='doge'))
		self.response_200(resp)
		self.assertEqual(resp.context['total_balance'], 4433416)
		self.assertEqual(resp.context['symbol'], 'doge')

	def test_queryset(self):
		login = self.client.login(
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
		login = self.client.login(
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
			return_value = {
				'private': '678a45c9c579c1166278e53bb84648e0eb52d16239a411e95d7a2ae018d609ba',
				'wif': 'BroJJwWLvoS5e1nNzauUNPEdGB7f1vouheydRRcFyvYFgUEHxgc4',
				'address': 'C1pyYVnmoCXH5upC2x52CoVJ5R74mQWUqZ',
				'public': '03efb85b737b198e3fdd7080ffc4b3e3162e58c3a024d020d2d87cd53d410620ad'
			}
		)
		blockcypher.get_address_overview = mock.MagicMock(return_value=
			{
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
		login = self.client.login(
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
		login = self.client.login(
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
		self.bcy = factories.BcyFactory(user = self.user)
		blockcypher.generate_new_address = mock.MagicMock(
			return_value = {
				'private': '678a45c9c579c1166278e53bb84648e0eb52d16239a411e95d7a2ae018d609ba',
				'wif': 'BroJJwWLvoS5e1nNzauUNPEdGB7f1vouheydRRcFyvYFgUEHxgc4',
				'address': 'C1pyYVnmoCXH5upC2x52CoVJ5R74mQWUqZ',
				'public': '03efb85b737b198e3fdd7080ffc4b3e3162e58c3a024d020d2d87cd53d410620ad'
			}
		)
		blockcypher.get_address_overview = mock.MagicMock(return_value=
			{
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
		
		login = self.client.login(
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
		logout = self.client.logout()
		resp = self.get('/wallets/bcy/{}/_detail/'.format(self.bcy.address))
		self.response_403(resp)
		'''
		self.assertRedirects(
			resp,
			'/accounts/login/?next=/wallets/bcy/{}/_detail/'.format(self.bcy.address),
			fetch_redirect_response=False
		)
		'''

	def test_success_if_logged_in(self):
		resp = self.get( #'/wallets/bcy/C1pyYVnmoCXH5upC2x52CoVJ5R74mQWUqZ/_detail/'
			self.reverse(
				'wallets:detail',
				wallet = 'bcy',
				address = '{}'.format(self.bcy.address)
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
				wallet = 'bcy',
				address = '{}'.format(self.bcy.address)
			)
		)
		self.response_200(resp)
		self.assertTemplateUsed(resp, 'wallets/detail.html')
	
	def test_with_invalid_wallet(self):
		resp = self.get(
			self.reverse(
				'wallets:detail',
				wallet = 'FAKE',
				address = '{}'.format(self.bcy.address)
			)
		)
		self.response_404(resp)
	
	def test_post_withdraw_form_with_valid_data(self):
		api.not_simple_spend = mock.MagicMock(
			return_value='7981c7849294648c1e79dd16077a388b808fcf8c20035aec7cc5315b37dacfee'
		)
		resp = self.post(
			self.reverse(
				'wallets:detail',
				wallet = 'bcy',
				address = '{}'.format(self.bcy.address)
			),
			data = {
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
			'Transaction successfully created 7981c7849294648c1e79dd16077a388b808fcf8c20035aec7cc5315b37dacfee'
		)
	
	def test_post_withdraw_form_with_invalid_data(self):
		api.not_simple_spend = mock.MagicMock(
			return_value='7981c7849294648c1e79dd16077a388b808fcf8c20035aec7cc5315b37dacfee'
		)
		resp = self.post(
			self.reverse(
				'wallets:detail',
				wallet = 'bcy',
				address = '{}'.format(self.bcy.address)
			),
			data = {
				'address': '{}'.format(self.bcy.address),
				'amount': 1
			}
		)
		self.response_200(resp)
		self.assertEqual(
			len(resp.context['form'].errors),
			1
		)
	
'''
class TestWalletsWithdrawView(TestCase):

	def setUp(self):
		self.user = factories.UserFactory()
		blockcypher.generate_new_address = mock.MagicMock(
			return_value = {
				'private': '678a45c9c579c1166278e53bb84648e0eb52d16239a411e95d7a2ae018d609ba',
				'wif': 'BroJJwWLvoS5e1nNzauUNPEdGB7f1vouheydRRcFyvYFgUEHxgc4',
				'address': 'C1pyYVnmoCXH5upC2x52CoVJ5R74mQWUqZ',
				'public': '03efb85b737b198e3fdd7080ffc4b3e3162e58c3a024d020d2d87cd53d410620ad'
			}
		)
		blockcypher.get_address_overview = mock.MagicMock(return_value=
			{
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
		login = self.client.login(
			username='{}'.format(self.user.username),
			password='password'
		)
		self.resp = self.get(self.reverse('wallets:create', wallet='bcy'))		
		self.assertEqual(self.resp.status_code, 302)
		blockcypher.simple_spend = mock.MagicMock(return_value='7981c7849294648c1e79dd16077a388b808fcf8c20035aec7cc5315b37dacfee')


	def test_view_url_exists_at_desired_location(self):
		resp = self.get('/wallets/bcy/{}/_withdraw/'.format(self.bcy.address))
		self.response_302(resp)

	def test_redirect_if_not_logged_in(self):
		logout = self.client.logout()
		resp = self.get('/wallets/bcy/{}/_withdraw/'.format(self.bcy.address))
		self.assertRedirects(
			resp,
			'/accounts/login/?next=/wallets/bcy/{}/_withdraw/'.format(self.bcy.address),
			fetch_redirect_response=False
		)

	def test_success_if_logged_in(self):
		resp = self.get(
			self.reverse(
				'wallets:withdraw',
				wallet = 'bcy',
				address = '{}'.format(self.bcy.address)
			)
		)
		self.response_302(resp)
		self.assertRedirects(
			resp,
			'/wallets/bcy/{}/_detail/'.format(self.bcy.address),
			fetch_redirect_response=False
		)

	def test_post_if_not_logged_in(self):
		logout = self.client.logout()
		resp = self.post('/wallets/bcy/{}/_withdraw/'.format(self.bcy.address))
		self.assertRedirects(
			resp,
			'/accounts/login/?next=/wallets/bcy/{}/_withdraw/'.format(self.bcy.address),
			fetch_redirect_response=False
		)
	
	def test_post_with_valid_data(self):
		resp = self.post(
			'/wallets/bcy/{}/_withdraw/'.format(self.bcy.address),
			{'amount': 0, 'address': '{}'.format(self.bcy.address)}
		)
		self.assertRedirects(
			resp,
			'/wallets/bcy/{}/_detail/'.format(self.bcy.address),
		)		
	
	def test_post_if_not_logged_in_without_data(self):
		resp = self.post('/wallets/bcy/{}/_withdraw/'.format(self.bcy.address))
		self.assertRedirects(
			resp,
			'/accounts/login/?next=/wallets/bcy/{}/_withdraw/'.format(self.bcy.address),
			fetch_redirect_response=False
		)
'''

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
				'transaction_id': '0e497d00057a2ae14e6e3f0d413173dbfa9f2f0a05114764aeaa9e88fa4a5d05',
				'payload': None
			}
		self.signature = signing.dumps(self.data)

	def test_post_with_invalid_signature(self):
		#resp = self.post('/wallets/webhook/{}/'.format(self.fake_signature))
		#self.response_200(resp)
		self.assertRaises(
			AssertionError,
			self.post,
			'/wallets/webhook/{}/'.format(self.fake_signature)
		)
	
	def test_post_with_valid_signature(self):
		resp = self.post('/wallets/webhook/{}/'.format(self.signature))
		self.response_200(resp)

	def test_extract_webhook_id(self):
		data = {
				'from_address': 'C2ATnDcRHEeEceUNY1wWjQAtxQK3kGfoZ9',
				'to_addresses': ['CDHsAcdbWvwtBaM9urmRU2VpQ3yMXfoUjy'],
				'symbol': 'bcy',
				'event': 'confirmed-tx',
				'transaction_id': '1e497d00057a2ae14e6e3f0d413173dbfa9f2f0a05114764aeaa9e88fa4a5d05',
				'payload': None
			}
		signature = signing.dumps(self.data)
		resp = self.post('/wallets/webhook/{}/'.format(signature))
		self.response_200(resp)

	def test_unsubscribe_from_webhook(self):
		blockcypher.list_webhooks = mock.MagicMock(return_value=[
				{
					'address': 'C2ATnDcRHEeEceUNY1wWjQAtxQK3kGfoZ9',
					'callback_errors': 0,
					'event': 'confirmed-tx',
					'id': '35e06a63-b09b-4cb2-a536-208642c96cd4',
					'token': '75ada547a1524310971733088eb068ec',
					'url': 'http://localhost//wallets/webhook/{}/'.format(self.signature)
				}
			]
		)
		webhook_id = mock.MagicMock(return_value='35e06a63-b09b-4cb2-a536-208642c96cd4')
		blockcypher.unsubscribe_from_webhook = mock.MagicMock(return_value=True)
		resp = self.post('/wallets/webhook/{}/'.format(self.signature))
		self.response_200(resp)
	

class TestInvoiceListView(TestCase):

	def setUp(self):
		self.user = factories.UserFactory()
		self.btc = factories.BtcFactory(user = self.user)
		self.ltc = factories.LtcFactory(user = self.user)
		self.dash = factories.DashFactory(user = self.user)
		self.doge = factories.DogeFactory(user = self.user)

		self.btc_invoice = factories.BtcInvoiceFactory(
			sender_wallet_object = self.btc,
			amount = [1]
			)
		self.btc_invoice.receiver_wallet_object.add(self.btc)
		self.btc_invoice.save()
		
		self.ltc_invoice = factories.LtcInvoiceFactory(
			sender_wallet_object = self.ltc,
			amount = [1]
			)
		self.ltc_invoice.receiver_wallet_object.add(self.ltc)
		self.ltc_invoice.save()

		self.dash_invoice = factories.DashInvoiceFactory(
			sender_wallet_object = self.dash,
			amount = [1]
			)
		self.dash_invoice.receiver_wallet_object.add(self.dash)
		self.dash_invoice.save()

		self.doge_invoice = factories.DogeInvoiceFactory(
			sender_wallet_object = self.doge,
			amount = [1]
			)
		self.doge_invoice.receiver_wallet_object.add(self.doge)
		self.doge_invoice.save()

	def test_redirect_if_not_logged_in(self):
		resp = self.get('/wallets/invoices/')
		self.assertRedirects(
			resp,
			'/accounts/login/?next=/wallets/invoices/',
			fetch_redirect_response=False
		)

	def test_success_if_logged_in(self):
		login = self.client.login(username = self.user.username, password = 'password')
		resp = self.get('/wallets/invoices/')
		self.response_200(resp)

	def test_context_object(self):
		login = self.client.login(username = self.user.username, password = 'password')
		resp = self.get('/wallets/invoices/')
		
		self.assertTrue(
			self.btc_invoice in self.get_context('btc_received_invoices'),
		)
		self.assertTrue(
			self.ltc_invoice in self.get_context('ltc_received_invoices'),
		)
		self.assertTrue(
			self.dash_invoice in self.get_context('dash_received_invoices'),
		)
		self.assertTrue(
			self.doge_invoice in self.get_context('doge_received_invoices'),
		)
		

	def test_view_uses_correct_template(self):
		login = self.client.login(
			username='{}'.format(self.user.username),
			password='password'
		)
		resp = self.get('/wallets/invoices/')		
		self.response_200(resp)
		self.assertTemplateUsed(resp, 'wallets/invoice_list.html')


class TestInvoiceDetailView(TestCase):
	
	def setUp(self):
		self.user = factories.UserFactory()
		self.btc = factories.BtcFactory(user = self.user)
		self.ltc = factories.LtcFactory(user = self.user)
		self.dash = factories.DashFactory(user = self.user)
		self.doge = factories.DogeFactory(user = self.user)

		self.btc_invoice = factories.BtcInvoiceFactory(
			sender_wallet_object = self.btc,
			amount = [1]
			)
		self.btc_invoice.receiver_wallet_object.add(self.btc)
		self.btc_invoice.save()
		
		self.ltc_invoice = factories.LtcInvoiceFactory(
			sender_wallet_object = self.ltc,
			amount = [1]
			)
		self.ltc_invoice.receiver_wallet_object.add(self.ltc)
		self.ltc_invoice.save()

		self.dash_invoice = factories.DashInvoiceFactory(
			sender_wallet_object = self.dash,
			amount = [1]
			)
		self.dash_invoice.receiver_wallet_object.add(self.dash)
		self.dash_invoice.save()

		self.doge_invoice = factories.DogeInvoiceFactory(
			sender_wallet_object = self.doge,
			amount = [1]
			)
		self.doge_invoice.receiver_wallet_object.add(self.doge)
		self.doge_invoice.save()

	def test_redirect_if_not_logged_in(self):
		resp = self.get('/wallets/invoices/1/')
		self.assertRedirects(
			resp,
			'/accounts/login/?next=/wallets/invoices/1/',
			fetch_redirect_response=False
		)

	def test_success_if_logged_in(self):
		login = self.client.login(username = self.user.username, password = 'password')
		resp = self.get('/wallets/invoices/{}/'.format(self.btc_invoice.pk))
		self.response_200(resp)
	
	def test_view_url_accessible_by_name(self):
		login = self.client.login(username = self.user.username, password = 'password')    	
		resp = self.get(self.reverse('wallets:invoice_detail', pk=self.btc_invoice.pk))
		self.assertEqual(resp.status_code, 200)		
	
	def test_context_object(self):
		login = self.client.login(username = self.user.username, password = 'password')
		resp = self.get('/wallets/invoices/{}/'.format(self.btc_invoice.pk))
		self.assertEqual(
			self.get_context('object'),
			self.btc_invoice
		)

	def test_object_belongs_user(self):
		login = self.client.login(username = self.user.username, password = 'password')
		resp = self.get('/wallets/invoices/{}/'.format(self.btc_invoice.pk))
		self.assertTrue(self.user in [wallet.user for wallet in self.get_context('object').receiver_wallet_object.all()])
		self.assertTrue(self.user in [wallet.user for wallet in self.btc_invoice.receiver_wallet_object.all()])
		
		self.assertEqual(
			self.get_context('object').sender_wallet_object.user,
			self.user
		)

	def test_view_uses_correct_template(self):
		login = self.client.login(
			username='{}'.format(self.user.username),
			password='password'
		)
		resp = self.get('/wallets/invoices/{}/'.format(self.btc_invoice.pk))
		self.response_200(resp)
		self.assertTemplateUsed(resp, 'wallets/invoice_detail.html')

	def test_permission_denied(self):
		user = factories.UserFactory()
		login = self.client.login(
			username='{}'.format(user.username),
			password='password'
		)
		resp = self.get('/wallets/invoices/{}/'.format(self.btc_invoice.pk))
		self.response_403(resp)		
	

class TestInvoicePayView(TestCase):
	def setUp(self):
		self.user = factories.UserFactory()
		self.btc = factories.BtcFactory(user = self.user)

		self.btc_invoice = factories.BtcInvoiceFactory(
			sender_wallet_object = self.btc,
			amount = [1]
			)
		self.btc_invoice.receiver_wallet_object.add(self.btc)
		self.btc_invoice.save()
		api.not_simple_spend = mock.MagicMock(return_value='7981c7849294648c1e79dd16077a388b808fcf8c20035aec7cc5315b37dacfee')
		blockcypher.subscribe_to_address_webhook = mock.MagicMock(return_value='bcaf7c39-9a7f-4e8b-8ba4-23b3c1806039')

	def test_redirect_if_not_logged_in(self):
		resp = self.get('/wallets/invoices/{}/_pay/'.format(self.btc_invoice.pk))
		self.response_403(resp)

	def test_success_if_logged_in(self):
		login = self.client.login(username = self.user.username, password = 'password')
		resp = self.get('/wallets/invoices/{}/_pay/'.format(self.btc_invoice.pk))
		self.response_200(resp)

	def test_view_url_accessible_by_name(self):
		login = self.client.login(username = self.user.username, password = 'password')    	
		resp = self.get(self.reverse('wallets:invoice_pay', pk=self.btc_invoice.pk))
		self.assertEqual(resp.status_code, 200)		
		
	def test_context_object(self):
		login = self.client.login(username = self.user.username, password = 'password')
		resp = self.get('/wallets/invoices/{}/_pay/'.format(self.btc_invoice.pk))
		self.assertEqual(
			self.get_context('object'),
			self.btc_invoice
		)
	
	def test_object_belongs_user(self):
		login = self.client.login(username = self.user.username, password = 'password')
		resp = self.get('/wallets/invoices/{}/_pay/'.format(self.btc_invoice.pk))
		self.assertTrue(self.user in [wallet.user for wallet in self.get_context('object').receiver_wallet_object.all()])
		self.assertTrue(self.user in [wallet.user for wallet in self.btc_invoice.receiver_wallet_object.all()])
		
		self.assertEqual(
			self.get_context('object').sender_wallet_object.user,
			self.user
		)

	def test_view_uses_correct_template(self):
		login = self.client.login(
			username='{}'.format(self.user.username),
			password='password'
		)
		api.not_simple_spend = mock.MagicMock(return_value='7981c7849294648c1e79dd16077a388b808fcf8c20035aec7cc5315b37dacfee')
		resp = self.get('/wallets/invoices/{}/_pay/'.format(self.btc_invoice.pk))
		self.response_200(resp)
		self.assertTemplateUsed(resp, 'wallets/invoice_detail.html')

	def test_permission_denied(self):
		user = factories.UserFactory()
		login = self.client.login(
			username='{}'.format(user.username),
			password='password'
		)
		resp = self.get('/wallets/invoices/{}/_pay/'.format(self.btc_invoice.pk))
		self.response_403(resp)