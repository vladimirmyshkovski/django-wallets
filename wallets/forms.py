from django import forms
from django.core import validators
from .utils import to_satoshi
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


class WithdrawForm(forms.Form):

	address = forms.CharField(required = True, max_length = 40)
	amount = forms.DecimalField(required = True)

	def __init__(self, *args, **kwargs):
		self.obj = kwargs.pop('obj', None)
		super(WithdrawForm, self).__init__(*args, **kwargs)


	def clean_amount(self):
		data = self.cleaned_data['amount']
		#Check date is greater than zero.
		if data <= 0:
			raise ValidationError(_('Amount must be greater than zero.'))

		return data

	def clean_address(self):
		data = self.cleaned_data['address']
		#Check date length is greater than 10.
		if len(data) <= 10:
			raise ValidationError(_('Number of characters must be greater than 10.'))

		#Check that the recipient's address is not equal to the sender's address
		if self.obj:
			if data == self.obj.address:
				raise ValidationError(_('The recipient\'s address and the sender\'s address must be different.'))

		return data

	def clean(self):
		cleaned_data = super().clean()

	def spend(self):
		if self.obj:
			address = self.cleaned_data['address']
			amount = self.cleaned_data['amount']
			transaction = self.obj.spend([address], [to_satoshi(float(amount))])
			return transaction
