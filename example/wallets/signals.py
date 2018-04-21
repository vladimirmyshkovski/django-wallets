from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.dispatch import Signal
from .services import generate_new_address

get_webhook = Signal(
		providing_args=[
			'from_address',
			'to_addresses',
			'symbol',
			'event',
			'transaction_id',
			'payload'
		]
	)