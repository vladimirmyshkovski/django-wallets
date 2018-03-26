withdraw_schema = {
	'amount': {
		'type': 'float',
		'min': 0.00000001,
		'coerce': float,
		'required': True,
		'empty': False
	},
	'address': {
		'type': 'string',
		'minlength': 5,
		'required': True,
		'empty': False
	},
}