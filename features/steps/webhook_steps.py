# -- FILE: features/steps/webhook_steps.py
from behave import given, when, then, step
from tests.factories import UserFactory, BtcFactory
from wallets.services import generate_new_address
from wallets.utils import from_satoshi
from wallets.signals import get_webhook
from django.conf import settings
import blockcypher
import time
from django.core import signing
from django.urls import reverse
import logging
from django.dispatch import receiver
import mock


logger = logging.getLogger(__name__)


@given('2 unique users')
def step_impl(context):
	first_user = UserFactory()
	second_user = UserFactory()
	print(first_user)
	print(second_user)
	context.first_user = first_user
	context.second_user = second_user
	
	generate_new_address(user=first_user, coin_symbol='bcy')
	generate_new_address(user=second_user, coin_symbol='bcy')
	
	context.test.assertNotEqual(
		first_user,
		None
	)
	context.test.assertNotEqual(
		second_user,
		None
	)

@when('the first user send to coins to second user and set webhook')
def step_impl(context):
	first_user_bcy_wallet = context.first_user.bcy_wallets.first()  
	second_user_bcy_wallet = context.second_user.bcy_wallets.first()
	context.test.assertNotEqual(
		first_user_bcy_wallet,
		None
	)
	context.test.assertNotEqual(
		second_user_bcy_wallet,
		None
	)
	
	blockcypher.send_faucet_coins(
		address_to_fund=first_user_bcy_wallet.address,
		satoshis=100000,
		api_key=settings.BLOCKCYPHER_API_KEY,
		coin_symbol='bcy'
	)
	time.sleep(60)
	signature = mock.MagicMock(return_value='eyJldmVudCI6ImNvbmZpcm1lZC10eCIsInN5bWJvbCI6ImJjeSIsInRvX2FkZHJlc3MiOiJDN3FtQlN1dTlMTFF3RHhpZ0ZiMTRMeGRTSFBOVW9mbWtiIiwiZnJvbV9hZGRyZXNzIjoiQnZlU2lDdERkOGIyTVFnbkRCRTlkWWgyOTlNZGNzZXg1MyIsInRyYW5zYWN0aW9uX2lkIjoiYTc3NmZiNmIxZWY2NTZkZDBiNmI4ZTUyOGIzMTA3ZWM5NWY5Njc0ZWQ1ZDMyMWM2YTgzOTY3YjhkNzE0MGJjOCJ9:1f3nBn:5zSoXFPi8SKut2mHrTn9FDZMTYw')
	
	context.transaction = first_user_bcy_wallet.spend_with_webhook(address=second_user_bcy_wallet.address, amount=from_satoshi(1000))
	
	context.test.assertNotEqual(
		context.transaction,
		None
	)
	
	blockcypher.list_webhooks = mock.MagicMock(return_value=[
			{
				'address': 'BuHUupxf4UdHStZvhtrjmncFa8NhFCLB1x',
				'event': 'confirmed-tx',
				'callback_errors': 0,
				'token': '75ada547a1524310971733088eb068ec',
				'url': 'https://localhost/wallets/webhook/eyJ0cmFuc2FjdGlvbl9pZCI6IjA5N2YzNjQ2NDVlZjExYWNlNTE1MjQ0ZmUyMGM4ZDdhNGUxZGFiYjRiNGE2ZDNlNTQyMDMwNzQyYTA5MmEzYzgiLCJmcm9tX2FkZHJlc3MiOiJCdUhVdXB4ZjRVZEhTdFp2aHRyam1uY0ZhOE5oRkNMQjF4Iiwic3ltYm9sIjoiYmN5IiwidG9fYWRkcmVzcyI6IkMxQ2FNVmh4VHlpRm01ZW1DamdqV0htNUNzdG9pb1pMcFUiLCJldmVudCI6ImNvbmZpcm1lZC10eCJ9:1f3n8X:ZofyAC2ihv1WN86PXYwAh-ZqM0E/',
				'id': 'b8224122-28bf-47cf-be3c-48677acb9fd5'
			},
			{
				'address': 'BveSiCtDd8b2MQgnDBE9dYh299Mdcsex53',
				'event': 'confirmed-tx',
				'callback_errors': 0,
				'token': '75ada547a1524310971733088eb068ec',
				'url': 'https://localhost/wallets/webhook/eyJldmVudCI6ImNvbmZpcm1lZC10eCIsInN5bWJvbCI6ImJjeSIsInRvX2FkZHJlc3MiOiJDN3FtQlN1dTlMTFF3RHhpZ0ZiMTRMeGRTSFBOVW9mbWtiIiwiZnJvbV9hZGRyZXNzIjoiQnZlU2lDdERkOGIyTVFnbkRCRTlkWWgyOTlNZGNzZXg1MyIsInRyYW5zYWN0aW9uX2lkIjoiYTc3NmZiNmIxZWY2NTZkZDBiNmI4ZTUyOGIzMTA3ZWM5NWY5Njc0ZWQ1ZDMyMWM2YTgzOTY3YjhkNzE0MGJjOCJ9:1f3nBm:19f0N3vJNNRADNtBNeszrruc0BA/',
				'id': 'dbe0bd20-9e25-4649-b2ae-d6e388d94e74'
			}
		]
	)

	def handler(sender, kwargs):
		print('KWARGS: ' + str(kwargs))

	context.response = context.test.client.post(reverse('wallets:webhook', kwargs={'signature': signature}))


	get_webhook.connect(handler)
	time.sleep(10)
	get_webhook.disconnect(handler)

@then('the second user checks his address, and his balance is greater than {number:d}')
def step_impl(context, number):
	time.sleep(60)
	second_user_bcy_wallet = context.second_user.bcy_wallets.first()

	def handler(sender, total, **kwargs):
		context.test.assertTrue(second_user_bcy_wallet.balance > number)
	

@then('remove webhook')
def step_impl(context):
	pass
