from django.dispatch import Signal

get_webhook = Signal(
    providing_args=[
        'from_address',
        'to_addresses',
        'symbol',
        'event',
        'transaction_id',
        'invoice_id',
        'content_object'
    ]
)

invoice_is_paid = Signal(
    providing_args=[
        'invoice_id'
    ]
)
