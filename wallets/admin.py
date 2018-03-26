from django.contrib import admin
from .models import Btc, Ltc, Dash, Doge

class BaseWalletAdmin(admin.ModelAdmin):
	list_display = ['user', 'address']
	exclude = ['private']
	readonly_fields = ['public', 'address', 'wif', 'coin_symbol','coin_name']

@admin.register(Btc)
class BtcAdmin(BaseWalletAdmin):
	pass

@admin.register(Ltc)
class LtcAdmin(BaseWalletAdmin):
	pass

@admin.register(Dash)
class DashAdmin(BaseWalletAdmin):
	pass

@admin.register(Doge)
class DogeAdmin(BaseWalletAdmin):
	pass