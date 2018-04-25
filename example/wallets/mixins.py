from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Bcy, Btc, Ltc, Doge, Dash


class OwnerPermissionsMixin(LoginRequiredMixin):

    def dispatch(self, request, *args, **kwargs):
        if hasattr(self, 'get_object'):
            obj = self.get_object()
            if obj.user != self.request.user:
                raise PermissionDenied()
        return super(OwnerPermissionsMixin, self).dispatch(request, *args,
                                                           **kwargs)


class CheckWalletMixin():

    def check_wallet(self, symbol):
        if symbol == 'btc':
            model = Btc
        elif symbol == 'bcy':
            return Bcy
        elif symbol == 'ltc':
            model = Ltc
        elif symbol == 'dash':
            model = Dash
        elif symbol == 'doge':
            model = Doge
        else:
            model = None
        return model
