#import environ
import string
import random
import logging
import requests
import blockcypher
from django.core import signing
from django.core.signing import BadSignature, SignatureExpired

from django.conf import settings

from django.contrib.contenttypes.models import ContentType


domain = settings.DOMAIN_NAME
api_key = settings.BLOCKCYPHER_API_KEY
#env = environ.Env()
logger = logging.getLogger(__name__)
#domain = env('DOMAIN_NAME')
#api_key = env('BLOCKCYPHER_API_KEY')



def to_satoshi(amount):
	if type(amount) is float:
		return int(amount * 100000000)
	else:
		return amount 

def from_satoshi(amount):
	return float(amount / 100000000)

def set_webhook(symbol, from_address, to_address, transaction_id):
	pass

def decode_signin(signature):
	sign = None
	try:
		sign = signing.loads(signature, max_age=60*60*24*30)
	except SignatureExpired:
		logger.exception("Signature expired")
	except BadSignature:
		logger.exception("Signature invalid")
	return sign	

def extract_webhook_id(signature, coin_symbol):
	webhook_id = None
	webhooks = blockcypher.list_webhooks(api_key, coin_symbol=coin_symbol)
	for webhook in webhooks:
		if webhook['url'] == 'https://{}/wallets/webhook/{}/'.format(domain, signature):
			webhook_id = webhook['id'] 
	return webhook_id

def unsubscribe_from_webhook(webhook_id):
	unsubscribe = blockcypher.unsubscribe_from_webhook(webhook_id)
	return unsubscribe

def parse_requset(request):
	data = request.body.decode('utf-8')
	result = {}
	if len(data.split('&')) > 0:
		for item in data.split('&'):
			if len(item.split('=')) > 0:
				key = item.split('=')[0]
				value = item.split('=')[1]
				result[key] = value
	if 'csrfmiddlewaretoken' in result:
		result.pop('csrfmiddlewaretoken')
	return result

def parse_errors(errors):
	error_list = []
	for error in errors:
		error_string = '{} field {}'.format(error.capitalize(), errors[error][0])
		error_list.append(error_string)	
	return ', '.join(error_list)


class GetWebhook(object):
	"""docstring for GetWebhook"""
	def __init__(self, signal):
		super(GetWebhook, self).__init__()
		self.signal = signal
		self.from_address = None
		self.to_address = None
		self.symbol = None
		self.event = None
		self.transaction_id = None
		self.wallet = None
		parse_signal()
		get_object()

	def parse_signal(self):
		if self.signal:
			if 'from_address' im self.signal:
				self.from_address = self.sigal['from_address']
			if 'to_address' in self.signal:
				self.to_address = self.signal['to_address']
			if 'symbol' in self.signal:
				self.symbol = signal['symbol']
			if 'event' in self.signal:
				self.event = signal['event']
			if 'transaction_id' in self.signal:
				self.transaction_id = self.signal['transaction_id']
	
	def get_object(self):
		if self.symbol:
			wallet_content_type = ContentType.objects.get(app_label="wallets", model=self.symbol.lower())
			wallet_object = wallet_content_type.get_object_for_this_type(address=self.from_address)
			self.wallet = wallet_object
	

class CheckTransactionConfirmations(GetWebhook):
	"""docstring for CheckTransactionConfirmations"""
	def __init__(self, confirmations=6):
		super(CheckTransactionConfirmations, self).__init__()
		#self.tx_hash = tx_hash
		self.confirmations = confirmations
		self.confirmed = False
		self.transaction = None
		self.processing()

	def find_transaction(self):
		tx_refs = self.wallet.transactions
		if transaction_id in tx_refs:
			self.transaction = tx_refs[transaction_id]

	def check_confirmations(self):
		if self.transaction:
			if self.transaction['confirmations'] >= self.confirmations:
				self.confirmed = True

	def processing(self):
		self.find_transaction()
		self.check_confirmations()