from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
from .models import Btc, Ltc, Dash, Doge
from django.dispatch import Signal

get_webhook = Signal(providing_args=['from_address', 'to_address', 'symbol', 'event', 'transaction_id'])


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_etc_and_btc(sender, instance, created, **kwargs):
	if created:
		btc = Btc.objects.create(user=instance)
		ltc = Ltc.objects.create(user=instance)
		dash = Dash.objects.create(user=instance)
		doge = Doge.objects.create(user=instance)
