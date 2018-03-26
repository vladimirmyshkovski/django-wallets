from rest_framework import serializers
from .models import Btc, Ltc, Dash, Doge#, Bcy


class WithdrawSerializer(serializers.Serializer):

	amount = serializers.IntegerField()
	address = serializers.CharField()


class BtcSerializer(serializers.ModelSerializer):
	class Meta:
		model = Btc
		fields = ['public', 'address', 'wif', 'user', 'coin_symbol', 
				'coin_name', 'balance', 'created', 'modified', 'id',
				'rate']


class LtcSerializer(serializers.ModelSerializer):

	class Meta:
		model = Btc
		fields = ['public', 'address', 'wif', 'user', 'coin_symbol', 
				'coin_name', 'balance', 'created', 'modified', 'id',
				'rate']

class DashSerializer(serializers.ModelSerializer):

	class Meta:
		model = Btc
		fields = ['public', 'address', 'wif', 'user', 'coin_symbol', 
				'coin_name', 'balance', 'created', 'modified', 'id',
				'rate']

class DogeSerializer(serializers.ModelSerializer):
	class Meta:
		model = Btc
		fields = ['public', 'address', 'wif', 'user', 'coin_symbol', 
				'coin_name', 'balance', 'created', 'modified', 'id',
				'rate']
'''
class BcySerializer(serializers.ModelSerializer):

	class Meta:
		model = Btc
		fields = ['public', 'address', 'wif', 'user', 'coin_symbol', 
				'coin_name', 'balance', 'is_removed', 'modified', 'id',
				'rate']
'''
class WalletSerializer(serializers.RelatedField):
	
	def to_representation(self, value):
		if isinstance(value, Btc):
			serializer = BtcSerializer(value)
		elif isinstance(value, Ltc):
			serializer = LtcSerializer(value)
		elif isinstance(value, Dash):
			serializer = DashSerializer(value)
		elif isinstance(value, Doge):
			serializer = DogeSerializer(value)
		#elif isinstance(value, Bcy):
		#	serializer = BcySerializer(value)
		else:
			raise Exception('Unexpected type of tagged object')
		return	serializer.data
	
	'''
	def to_internal_value(self, data):
		wallet_type = data.pop('wallet_type')

		if wallet_type == 'btc':
			serializer = BtcSerializer(data)
		elif wallet_type == 'ltc':
			serializer = LtcSerializer(data)
		elif wallet_type == 'dash':
			serializer = DashSerializer(data)
		elif wallet_type == 'doge':
			serializer = DogeSerializer(data)
		elif wallet_type == 'bcy':
			serializer = BcySerializer(data)
		else:
			raise serializers.ValidationError('No wallet_type provided')

		if serializer.is_valid():
			obj = serializer.save()
		else:
			raise serializers.ValidationError(serializer.errors)

		return obj
	'''