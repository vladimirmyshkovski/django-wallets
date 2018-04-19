import blockcypher
from django.contrib.auth import get_user_model
from .utils import get_wallet_model
from django.conf import settings
from itertools import chain

api_key = settings.BLOCKCYPHER_API_KEY

def generate_new_address(user, coin_symbol):
	if isinstance(user, get_user_model()) and get_wallet_model(coin_symbol):
		r = blockcypher.generate_new_address(coin_symbol=coin_symbol, api_key=api_key)
		obj = get_wallet_model(coin_symbol).objects.create(
			user = user,
			private = r['private'],
			public = r['public'],
			address = r['address'],
			wif = r['wif']
		)
		return obj
	else:
		return None

def get_wallet_invoices(invoices, wallets, symbol):
	received_invoices = []
	sended_invoices = []
	for wallet in wallets:
		for invoice in wallet.invoice_set.all():
			received_invoices.append(invoice)
		for invoice in wallet.sended_invoices.all():
			sended_invoices.append(invoice)

	#for invoice in invoices:
	#	for wallet in wallets:
	#		if invoice.receiver_wallet_object == wallet:
	#			received_invoices.append(invoice)
	#		elif invoice.sender_wallet_object == wallet:
	#			sended_invoices.append(invoice)
	result = {
		'{}_received_invoices'.format(symbol): received_invoices,
		'{}_sended_invoices'.format(symbol): sended_invoices
	}
	return result