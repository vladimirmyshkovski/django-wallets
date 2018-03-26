from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Btc, Ltc, Doge, Dash


class OwnerPermissions(LoginRequiredMixin):

    def get_object(self, *args, **kwargs):
        obj = super(OwnerPermissions, self).get_object(*args, **kwargs)
        if obj.user != self.request.user:
            raise PermissionDenied()
        else:
            return obj


class CheckWallet():
	
	def check_wallet(self, symbol):
		if symbol == 'btc':
			model = Btc
		elif symbol == 'ltc':
			model = Ltc
		elif symbol == 'dash':
			model = Dash
		elif symbol == 'doge':
			model = Doge
		else:
			model = None
		return model