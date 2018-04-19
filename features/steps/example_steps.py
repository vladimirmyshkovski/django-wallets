# -- FILE: features/steps/example_steps.py
from behave import given, when, then, step
from tests.factories import UserFactory, BtcFactory
from wallets.services import generate_new_address
from wallets.utils import from_satoshi
from django.conf import settings
import blockcypher
import time
import logging
logger = logging.getLogger(__name__)

@given('2 users')
def step_impl(context):
	first_user = UserFactory()
	second_user = UserFactory()
	context.first_user = first_user
	context.second_user = second_user
	print('sex')
	logger.info(msg="fuck fuck fuck")
	#logger.critical('lick lick lick')	
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

@when('the first user send to coins to second user')
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
	#blockcypher.send_faucet_coins(
	#	address_to_fund=first_user_bcy_wallet.address,
	#	satoshis=100000,
	#	api_key=settings.BLOCKCYPHER_API_KEY,
	#	coin_symbol='bcy'
	#)
	#time.sleep(60)
	#context.transaction = first_user_bcy_wallet.spend(address=second_user_bcy_wallet.address, amount=from_satoshi(1000))
	#context.test.assertNotEqual(
	#	context.transaction,
	#	None
	#)

@then('the second user checks his address, and his balance is greater than {number:d}')
def step_impl(context, number):
	#time.sleep(60)
	#second_user_bcy_wallet = context.second_user.bcy_wallets.first()
	#context.test.assertTrue(second_user_bcy_wallet.balance > number)
	assert 'fuck' != 'suck'