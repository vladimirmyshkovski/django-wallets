from django.test import TestCase
from wallets import utils
from wallets import models
from django.core import signing
from django.core.signing import BadSignature, SignatureExpired
from . import factories
import mock
import itertools
import blockcypher


class TestToSatoshi(TestCase):
	
	def setUp(self):

		self.right_amount = 0.00000001
		self.wrong_amount = 1
		self.right_string_amount = '0.00000001'
		self.wrong_string_amount = 'WRONG_STRING'


	def test_right_amount(self):
		amount = utils.to_satoshi(self.right_amount)
		self.assertEqual(
			amount,
			1
		)
		self.assertTrue(
			type(amount),
			int(1)
		)
		
	def test_wrong_amount(self):
		self.assertRaises(
			ValueError,
			utils.to_satoshi,
			self.wrong_amount
		)
		self.assertRaisesRegex(
			ValueError,
			'Amount must be float',
			lambda: utils.to_satoshi(self.wrong_amount),
		)
	
	def test_right_string_amount(self):
		amount = utils.to_satoshi(self.right_string_amount)
		self.assertEqual(
			amount,
			1
		)
		self.assertTrue(
			type(amount),
			int(1)
		)
	
	def test_wrong_string_amount(self):
		self.assertRaises(
			ValueError,
			utils.to_satoshi,
			self.wrong_string_amount
		)
		self.assertRaisesRegex(
			ValueError,
			'Can not convert string to float',
			lambda: utils.to_satoshi(self.wrong_string_amount),
		)		
		

class TestFromSatochi(TestCase):

	def setUp(self):

		self.right_amount = 100000000
		self.wrong_amount = 0.1
		self.right_string_amount = '100000000'
		self.wrong_string_amount = 'FAKE_STRING'

	def test_right_amount(self):
		amount = utils.from_satoshi(self.right_amount)
		self.assertEqual(
			amount,
			1
		)
		self.assertTrue(
			type(amount),
			int(1)
		)
		
	def test_wrong_amount(self):
		self.assertRaises(
			ValueError,
			utils.from_satoshi,
			self.wrong_amount
		)
		self.assertRaisesRegex(
			ValueError,
			'Amount must be integer',
			lambda: utils.from_satoshi(self.wrong_amount),
		)
	
	def test_right_string_amount(self):
		amount = utils.from_satoshi(self.right_string_amount)		
		self.assertEqual(
			amount,
			1
		)
		self.assertTrue(
			type(amount),
			int(1)
		)

	def test_wrong_string_amount(self):
		self.assertRaises(
			ValueError,
			utils.from_satoshi,
			self.wrong_string_amount
		)
		self.assertRaisesRegex(
			ValueError,
			'Can not convert string to float',
			lambda: utils.from_satoshi(self.wrong_string_amount),
		)


class TestDecodeSignin(TestCase):

	def setUp(self):
		self.data = {
				'from_address': 'FAKE_FROM_ADDRESS',
				'to_address': 'FAKE_TO_ADDRESS',
				'symbol': 'FAKE_SYMBOL',
				'event': 'FAKE_EVENT',
				'transaction_id': 'FAKE_TRANSACTION_ID'
			}
		self.signature = signing.dumps(self.data)

	def test_right_decode(self):
		signature = utils.decode_signin(self.signature)
		self.assertEqual(
			signature,
			self.data
		)
	
	def test_invalid_signature(self):
		self.assertRaises(
			BadSignature,
			utils.decode_signin,
			'FAKE_SIGNATURE'
		)

	def test_expired_signature(self):
		utils.decode_signin(self.signature, max_age=1)
		import time
		time.sleep(1)
		self.assertRaises(
			SignatureExpired,
			utils.decode_signin,
			self.signature,
			1
		)		
	

class TestExtractWebhookId(TestCase):
	
	def setUp(self):
		self.signature = 'eyJldmVudCI6ImNvbmZpcm1lZC10eCIsInN5bWJvbCI6ImJ0YyIsInRyYW5zYWN0aW9uX2lkIjoiNzk4MWM3ODQ5Mjk0NjQ4YzFlNzlkZDE2MDc3YTM4OGI4MDhmY2Y4YzIwMDM1YWVjN2NjNTMxNWIzN2RhY2ZlZSIsImZyb21fYWRkcmVzcyI6IjFITDdmakNSR0tDNEVmUFJqSFZnbUxtaTdCbXB1OGhHcHMiLCJ0b19hZGRyZXNzIjoiMUhMN2ZqQ1JHS0M0RWZQUmpIVmdtTG1pN0JtcHo4aEdwcyJ9:1f2yCy:2THNsZ9RadqZ35IYq2fH4hMCxdM'


	def test_with_valid_data(self):
		blockcypher.list_webhooks = mock.MagicMock(return_value=[
				{
					'address': '1HL7fjCRGKC4EfPRjHVgmLmi7Bmpu8hGps',
					'callback_errors': 0,
					'event': 'confirmed-tx',
					'id': '35e06a63-b09b-4cb2-a536-208642c96cd4',
					'token': '75ada547a1524310971733088eb068ec',
					'url': 'https://http://localhost//wallets/webhook/eyJmcm9tX2FkZHJlc3MiOiIxSEw3ZmpDUkdLQzRFZlBSakhWZ21MbWk3Qm1wdThoR3BzIiwiZXZlbnQiOiJjb25maXJtZWQtdHgiLCJ0cmFuc2FjdGlvbl9pZCI6Ijc5ODFjNzg0OTI5NDY0OGMxZTc5ZGQxNjA3N2EzODhiODA4ZmNmOGMyMDAzNWFlYzdjYzUzMTViMzdkYWNmZWUiLCJ0b19hZGRyZXNzIjoiMUhMN2ZqQ1JHS0M0RWZQUmpIVmdtTG1pN0JtcHo4aEdwcyIsInN5bWJvbCI6ImJ0YyJ9:1f2yBc:Fh6c9r7bWmYBPk-gJCuXTPpkpXA/'
				},
				{
					'address': '1HL7fjCRGKC4EfPRjHVgmLmi7Bmpu8hGps',
					'callback_errors': 0,
					'event': 'confirmed-tx',
					'id': '8c125014-7d70-41ca-8ed1-4cc4264894e3',
					'token': '75ada547a1524310971733088eb068ec',
					'url': 'https://http://localhost//wallets/webhook/eyJldmVudCI6ImNvbmZpcm1lZC10eCIsInN5bWJvbCI6ImJ0YyIsInRyYW5zYWN0aW9uX2lkIjoiNzk4MWM3ODQ5Mjk0NjQ4YzFlNzlkZDE2MDc3YTM4OGI4MDhmY2Y4YzIwMDM1YWVjN2NjNTMxNWIzN2RhY2ZlZSIsImZyb21fYWRkcmVzcyI6IjFITDdmakNSR0tDNEVmUFJqSFZnbUxtaTdCbXB1OGhHcHMiLCJ0b19hZGRyZXNzIjoiMUhMN2ZqQ1JHS0M0RWZQUmpIVmdtTG1pN0JtcHo4aEdwcyJ9:1f2yCy:2THNsZ9RadqZ35IYq2fH4hMCxdM/'
				}
			]
		)
		webhook_id = utils.extract_webhook_id(self.signature, 'btc')
		self.assertNotEqual(
			webhook_id,
			None
		)

	def test_with_invalid_data(self):
		blockcypher.list_webhooks = mock.MagicMock(return_value=[
				{
					'address': '1HL7fjCRGKC4EfPRjHVgmLmi7Bmpu8hGps',
					'callback_errors': 0,
					'event': 'confirmed-tx',
					'id': '35e06a63-b09b-4cb2-a536-208642c96cd4',
					'token': '75ada547a1524310971733088eb068ec',
					'url': 'https://http://localhost//wallets/webhook/eyJmcm9tX2FkZHJlc3MiOiIxSEw3ZmpDUkdLQzRFZlBSakhWZ21MbWk3Qm1wdThoR3BzIiwiZXZlbnQiOiJjb25maXJtZWQtdHgiLCJ0cmFuc2FjdGlvbl9pZCI6Ijc5ODFjNzg0OTI5NDY0OGMxZTc5ZGQxNjA3N2EzODhiODA4ZmNmOGMyMDAzNWFlYzdjYzUzMTViMzdkYWNmZWUiLCJ0b19hZGRyZXNzIjoiMUhMN2ZqQ1JHS0M0RWZQUmpIVmdtTG1pN0JtcHo4aEdwcyIsInN5bWJvbCI6ImJ0YyJ9:1f2yBc:Fh6c9r7bWmYBPk-gJCuXTPpkpXA/'
				},
				{
					'address': '1HL7fjCRGKC4EfPRjHVgmLmi7Bmpu8hGps',
					'callback_errors': 0,
					'event': 'confirmed-tx',
					'id': '8c125014-7d70-41ca-8ed1-4cc4264894e3',
					'token': '75ada547a1524310971733088eb068ec',
					'url': 'https://http://localhost//wallets/webhook/eyJldmVudCI6ImNvbmZpcm1lZC10eCIsInN5bWJvbCI6ImJ0YyIsInRyYW5zYWN0aW9uX2lkIjoiNzk4MWM3ODQ5Mjk0NjQ4YzFlNzlkZDE2MDc3YTM4OGI4MDhmY2Y4YzIwMDM1YWVjN2NjNTMxNWIzN2RhY2ZlZSIsImZyb21fYWRkcmVzcyI6IjFITDdmakNSR0tDNEVmUFJqSFZnbUxtaTdCbXB1OGhHcHMiLCJ0b19hZGRyZXNzIjoiMUhMN2ZqQ1JHS0M0RWZQUmpIVmdtTG1pN0JtcHo4aEdwcyJ9:1f2yCy:2THNsZ9RadqZ35IYq2fH4hMCxdM/'
				}
			]
		)
		webhook_id = utils.extract_webhook_id('FAKE_WEBHOOK', 'btc')
		self.assertEqual(
			webhook_id,
			None
		)


class TestUnsubscribeFromWebhook(TestCase):
	
	def setUp(self):
		pass


	def test_with_valid_data(self):
		blockcypher.unsubscribe_from_webhook = mock.MagicMock(return_value=True)
		unsubscribe = utils.unsubscribe_from_webhook('8c125014-7d70-41ca-8ed1-4cc4264894e3', coin_symbol='btc')
		self.assertTrue(unsubscribe)


class TestSetWebhook(TestCase):

	def setUp(self):
		pass

	def test_with_valid_data(self):
		signing.dumps = mock.MagicMock(return_value='eyJldmVudCI6ImNvbmZpcm1lZC10eCIsInN5bWJvbCI6ImJ0YyIsInRyYW5zYWN0aW9uX2lkIjoiNzk4MWM3ODQ5Mjk0NjQ4YzFlNzlkZDE2MDc3YTM4OGI4MDhmY2Y4YzIwMDM1YWVjN2NjNTMxNWIzN2RhY2ZlZSIsImZyb21fYWRkcmVzcyI6IjFITDdmakNSR0tDNEVmUFJqSFZnbUxtaTdCbXB1OGhHcHMiLCJ0b19hZGRyZXNzIjoiMUhMN2ZqQ1JHS0M0RWZQUmpIVmdtTG1pN0JtcHo4aEdwcyJ9')
		blockcypher.subscribe_to_address_webhook = mock.MagicMock(return_value='8c125014-7d70-41ca-8ed1-4cc4264894e3')
		webhook_id = utils.set_webhook(
			from_address='FAKE_FROM_ADDRESS',
			to_address='FAKE_TO_ADDRESS',
			transaction_id='FAKE_TRANSACTION_ID',
			coin_symbol='FAKE_COIN_SYMBOL',
			event='FAKE_EVENT'
		)
		self.assertEqual(
			type(webhook_id),
			type('')
		)


class TestGetWalletModel(TestCase):

	def setUp(self):
		self.btc = factories.BtcFactory
		self.ltc = factories.LtcFactory
		self.dash = factories.DashFactory
		self.doge = factories.DogeFactory

	def test_with_valid_data(self):
		btc = utils.get_wallet_model('btc')
		ltc = utils.get_wallet_model('ltc')
		dash = utils.get_wallet_model('dash')
		doge = utils.get_wallet_model('doge')
		
		self.assertEqual(btc, models.Btc)
		self.assertEqual(ltc, models.Ltc)
		self.assertEqual(dash, models.Dash)
		self.assertEqual(doge, models.Doge)
		
	def test_with_invalid_data(self):
		fake = utils.get_wallet_model('fake')

		self.assertEqual(fake, None)


class TestGetWebhook(TestCase):

	def setUp(self):
		factories.BtcFactory()
		self.signal = {
			'from_address': '{}'.format(models.Btc.objects.order_by('?').first().address),
			'to_addresses': ['{}'.format(models.Btc.objects.order_by('?').first().address)],
			'symbol': 'btc',
			'event': 'confirmed-tx',
			'transaction_id': '4cff011ec53022f2ae47197d1a2fd4a6ac2a80139f4d0131c1fed625ed5dc869'
		}

	def test_with_valid_data(self):
		get_webhook = utils.GetWebhook(self.signal)
		self.assertTrue(isinstance(get_webhook.sender_wallet, models.Btc))
		self.assertTrue(isinstance(get_webhook.receiver_wallets[0], models.Btc))
	
	def test_with_invalid_data(self):
		get_webhook = utils.GetWebhook('FAKE_SIGNAL')
		self.assertEqual(get_webhook.sender_wallet, None)
		self.assertEqual(get_webhook.receiver_wallets, [])


class TestCheckTransactionConfirmations(TestCase):

	def setUp(self):
		self.wallet = factories.BtcFactory()
		self.signal = {
			'from_address': '{}'.format(models.Btc.objects.order_by('?').first().address),
			'to_addresses': ['{}'.format(models.Btc.objects.order_by('?').first().address)],
			'symbol': 'btc',
			'event': 'confirmed-tx',
			'transaction_id': '4cff011ec53022f2ae47197d1a2fd4a6ac2a80139f4d0131c1fed625ed5dc869'
		}

	def test_with_valid_data(self):
		blockcypher.get_address_details = mock.MagicMock(return_value=
			{
			    "address": "1DEP8i3QJCsomS4BSMY2RpU1upv62aGvhD", 
			    "balance": 4433416, 
			    "final_balance": 4433416, 
			    "final_n_tx": 7, 
			    "n_tx": 7, 
			    "total_received": 4433416, 
			    "total_sent": 0, 
			    "tx_url": "https://api.blockcypher.com/v1/btc/main/txs/", 
			    "txrefs": [
			        {
			            "block_height": 302013, 
			            "confirmations": 77809, 
			            "confirmed": "datetime.datetime(2014, 5, 22, 3, 46, 25, 0, tzinfo=tzutc())", 
			            "double_spend": False, 
			            "ref_balance": 4433416, 
			            "spent": False, 
			            "tx_hash": "14b1052855bbf6561bc4db8aa501762e7cc1e86994dda9e782a6b73b1ce0dc1e", 
			            "tx_input_n": -1, 
			            "tx_output_n": 0, 
			            "value": 20213
			        }, 
			        {
			            "block_height": 302002, 
			            "confirmations": 77820, 
			            "confirmed": "datetime.datetime(2014, 5, 22, 2, 56, 8, 0, tzinfo=tzutc())", 
			            "double_spend": False, 
			            "ref_balance": 4413203, 
			            "spent": False, 
			            "tx_hash": "4cff011ec53022f2ae47197d1a2fd4a6ac2a80139f4d0131c1fed625ed5dc869", 
			            "tx_input_n": -1, 
			            "tx_output_n": 0, 
			            "value": 40596
			        }, 
			    ], 
			    "unconfirmed_balance": 0, 
			    "unconfirmed_n_tx": 0, 
			    "unconfirmed_txrefs": []
			}
		)
		ctc = utils.CheckTransactionConfirmations(self.signal)
		self.assertTrue(ctc.confirmed)
		self.assertEqual(
			type(ctc.transaction),
			type({})
		)

		blockcypher.get_address_details = mock.MagicMock(return_value=
			{
			    "address": "1DEP8i3QJCsomS4BSMY2RpU1upv62aGvhD", 
			    "balance": 4433416, 
			    "final_balance": 4433416, 
			    "final_n_tx": 7, 
			    "n_tx": 7, 
			    "total_received": 4433416, 
			    "total_sent": 0, 
			    "tx_url": "https://api.blockcypher.com/v1/btc/main/txs/", 
			    "txrefs": [
			        {
			            "block_height": 302013, 
			            "confirmations": 2, 
			            "confirmed": "datetime.datetime(2014, 5, 22, 3, 46, 25, 0, tzinfo=tzutc())", 
			            "double_spend": False, 
			            "ref_balance": 4433416, 
			            "spent": False, 
			            "tx_hash": "14b1052855bbf6561bc4db8aa501762e7cc1e86994dda9e782a6b73b1ce0dc1e", 
			            "tx_input_n": -1, 
			            "tx_output_n": 0, 
			            "value": 20213
			        }, 
			        {
			            "block_height": 302002, 
			            "confirmations": 1, 
			            "confirmed": "datetime.datetime(2014, 5, 22, 2, 56, 8, 0, tzinfo=tzutc())", 
			            "double_spend": False, 
			            "ref_balance": 4413203, 
			            "spent": False, 
			            "tx_hash": "4cff011ec53022f2ae47197d1a2fd4a6ac2a80139f4d0131c1fed625ed5dc869", 
			            "tx_input_n": -1, 
			            "tx_output_n": 0, 
			            "value": 40596
			        }, 
			    ], 
			    "unconfirmed_balance": 0, 
			    "unconfirmed_n_tx": 0, 
			    "unconfirmed_txrefs": []
			}
		)
		ctc = utils.CheckTransactionConfirmations(self.signal)		
		self.assertFalse(ctc.confirmed)


	def test_with_invalid_data(self):

		ctc = utils.CheckTransactionConfirmations('FAKE_SIGNAL')
		self.assertFalse(ctc.confirmed)
		self.assertEqual(
			ctc.transaction,
			None
		)

	def tearDown(self):
		self.wallet.transactions = mock.MagicMock(return_value=[])
		#import pprint
		#pprint.pprint(self.wallet.__dict__['transactions']())


class TestConverter(TestCase):

	def setUp(self):
		pass

	def test_with_valid_data(self):
		currencies_list = ['btc', 'ltc', 'dash', 'doge']
		currencies = itertools.combinations(currencies_list, 2)
		for cuurency in currencies:
			
			converter = utils.Converter(
				cuurency[0],
				cuurency[1]
			)
			self.assertTrue(float(converter.result) > 0)

	def test_with_invalid_data(self):

		self.assertRaises(
			AssertionError,
			lambda: utils.Converter('btc', 'btc')
		)

		self.assertRaisesRegex(
			AssertionError,
			'It is not possible to convert btc to btc',
			lambda: utils.Converter('btc', 'btc')
		)

		self.assertRaises(
			AssertionError,
			lambda: utils.Converter('fake', 'btc')
		)

		self.assertRaisesRegex(
			AssertionError,
			'The converter is not provided for fake',
			lambda: utils.Converter('fake', 'btc')
		)

	def test_repr(self):
		converter = utils.Converter('btc', 'ltc')
		self.assertEqual(converter.__repr__(), str(converter.result))