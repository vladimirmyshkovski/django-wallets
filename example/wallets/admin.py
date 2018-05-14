from django.contrib import admin
from .models import Btc, Ltc, Dash, Doge, Bcy, ApiKey, Invoice, Payment


class BaseWalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'address']
    exclude = ['private']
    readonly_fields = ['public', 'address', 'wif', 'coin_symbol', 'coin_name']


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


@admin.register(Bcy)
class BcyAdmin(BaseWalletAdmin):
    pass


admin.site.register(ApiKey)
admin.site.register(Invoice)
admin.site.register(Payment)
