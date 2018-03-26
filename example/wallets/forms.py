from django import forms

class WithdrawForm(forms.Form):

	address = forms.CharField()
	amount = forms.DecimalField() 