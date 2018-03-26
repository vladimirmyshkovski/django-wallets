#import environ
import string
import random
import logging
import requests
import blockcypher
from django.core import signing
from django.core.signing import BadSignature, SignatureExpired

from django.conf import settings

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
		logger.exception("signature expired")
	except BadSignature:
		logger.exception("signature invalid")
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