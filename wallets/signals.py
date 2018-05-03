from django.dispatch import Signal

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
