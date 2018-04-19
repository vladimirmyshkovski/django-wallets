from django.test import TestCase
from .factories import UserFactory
from wallets import services
from wallets import models
from wallets import utils
import mock
from django.contrib.auth import get_user_model


class TestGenerateNewAddress(TestCase):

	def setUp(self):
		self.user = UserFactory()
	
	def test_without_data(self):
		self.assertRaises(
			TypeError,
			services.generate_new_address
		)

	def test_generate_new_address_with_valid_data(self):
		import blockcypher
		blockcypher.generate_new_address = mock.MagicMock(return_value={
            'address': '1HL7fjCRGKC4EfPRjHVgmLmi7Bmpu8hGps',
            'private': '2a9a2a50252bf2eb24553e70861e1774aa8507af1b9497e1da01fa0086a3dfb7',
            'public': '02053a352366b3bee2e3d0d29b346822706bdf7af3cd00f7ce9d3516010d4a37c4',
            'wif': 'KxeXM1gzy5PMJ47orJiZrBK89DycjPxbq7GVS1KcV7UKAFgFTQJx'
		})
		obj = services.generate_new_address(self.user, 'btc')
		self.assertTrue(
			isinstance(
				obj,
				models.Btc
			)
		)

	def test_generate_new_address_with_invalid_data(self):
		import blockcypher
		blockcypher.generate_new_address = mock.MagicMock(return_value={
            'address': '1HL7fjCRGKC4EfPRjHVgmLmi7Bmpu8hGps',
            'private': '2a9a2a50252bf2eb24553e70861e1774aa8507af1b9497e1da01fa0086a3dfb7',
            'public': '02053a352366b3bee2e3d0d29b346822706bdf7af3cd00f7ce9d3516010d4a37c4',
            'wif': 'KxeXM1gzy5PMJ47orJiZrBK89DycjPxbq7GVS1KcV7UKAFgFTQJx'
		})
		obj = services.generate_new_address(str(), 'btc')
		self.assertFalse(
			isinstance(
				obj,
				models.Btc
			)
		)		

	def tearDown(self):
		pass