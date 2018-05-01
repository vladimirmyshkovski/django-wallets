import factory
from wallets import models
from django.contrib.contenttypes.models import ContentType


class UserFactory(factory.django.DjangoModelFactory):

    username = factory.Sequence(lambda n: 'user-{}'.format(n))
    email = factory.Sequence(lambda n: 'user-{}@example.com'.format(n))
    password = factory.PostGenerationMethodCall('set_password', 'password')

    class Meta:
        model = 'auth.User'
        django_get_or_create = ('username', )


class BtcFactory(factory.django.DjangoModelFactory):

    user = factory.SubFactory(UserFactory)

    address = factory.Sequence(
        lambda n: '1HL7fjCRGKC4EfPRjHVgmLmi7Bmpu8hGps{}'.format(n))
    private = factory.Sequence(
        lambda n: '2a9a2a50252bf2eb24553e70861e1774aa8507af1b9497e1da01fa0086a3dfb7{}'.format(n))
    public = factory.Sequence(
        lambda n: '02053a352366b3bee2e3d0d29b346822706bdf7af3cd00f7ce9d3516010d4a37c4{}'.format(n))
    wif = factory.Sequence(
        lambda n: 'KxeXM1gzy5PMJ47orJiZrBK89DycjPxbq7GVS1KcV7UKAFgFTQJx{}'.format(n))

    class Meta:
        model = models.Btc


class LtcFactory(factory.django.DjangoModelFactory):

    user = factory.SubFactory(UserFactory)

    address = factory.Sequence(
        lambda n: 'LKn2NsN3iaGLguUeJs77r1v9eW8WupHrxc{}'.format(n))
    private = factory.Sequence(
        lambda n: '579e0ec5bda04c0b746c96e24e04acb57735feed8ccbc87f91291c0b3ea74348{}'.format(n))
    public = factory.Sequence(
        lambda n: '02b9d6ef88a28e865f0c1143c6158de5f3c6399585bf531fa4fa686d48c7d8f99b{}'.format(n))
    wif = factory.Sequence(
        lambda n: 'T5zJ18AZ9bwRCnA2ipng9YHANfAjZwhGvmRn6uxyoayatQ34aWft{}'.format(n))

    class Meta:
        model = models.Ltc


class DashFactory(factory.django.DjangoModelFactory):

    user = factory.SubFactory(UserFactory)

    address = factory.Sequence(
        lambda n: 'Xycnfonoprh1t9NyHDDiVNw4zZCmqzBJCm{}'.format(n))
    private = factory.Sequence(
        lambda n: '8816268d5b19cfbbec75aa28f41b2583d708364815c7b8901d889e0e39550b9d{}'.format(n))
    public = factory.Sequence(
        lambda n: '03afe0b3723958003ffd5599a92df93393ddc7903b7358b695d8c4d1212e5ab7cf{}'.format(n))
    wif = factory.Sequence(
        lambda n: 'XFrAdirzUf8qSjWNetnL2X3mve1CL8G4Cpqnc7MPYxnhpSysiXDE{}'.format(n))

    class Meta:
        model = models.Dash


class DogeFactory(factory.django.DjangoModelFactory):

    user = factory.SubFactory(UserFactory)

    address = factory.Sequence(
        lambda n: 'DFo6VWrYzuKv6WP2HxzXesJHb6ubjT9xt1{}'.format(n))
    private = factory.Sequence(
        lambda n: 'a9057b2bcc4b7ffa8a7abacf261fff5b34e2c52ea7e8eb41237c6371abbc4636{}'.format(n))
    public = factory.Sequence(
        lambda n: '02856bd93edf5088891c801fd8eba4244a2a2c2dbfbfa06d3fc6ef9439ed6daefc{}'.format(n))
    wif = factory.Sequence(
        lambda n: 'QUHBZKbsTZEuqUBb98X2obFpRY9TXy19sR5N4jzz2Ka2gm6n5JtE{}'.format(n))

    class Meta:
        model = models.Doge


class BcyFactory(factory.django.DjangoModelFactory):

    user = factory.SubFactory(UserFactory)

    address = factory.Sequence(
        lambda n: 'BvuiwCe7WZ8eD4P7ZNRs6zEU3K2okdNYm9{}'.format(n))
    private = factory.Sequence(
        lambda n: 'ca564b6f3c052865f733463675484ffdb6f4f7e2cc470925354790179cc9b013{}'.format(n))
    public = factory.Sequence(
        lambda n: '0288aae38aec430f0042d4886c913bbedc29a66d23990d684040bc2d258742814b{}'.format(n))
    wif = factory.Sequence(
        lambda n: 'Bv7M7hU3Z77zqkFmKoorhPwd2L3HAWHb1oxb1vDyVMjLCY39iNxR{}'.format(n))

    class Meta:
        model = models.Bcy


class InvoiceFactory(factory.django.DjangoModelFactory):

    wallet_id = factory.SelfAttribute('wallet.id')
    wallet_type = factory.LazyAttribute(
        lambda o: ContentType.objects.get_for_model(o.wallet)
    )
    tx_ref = '7981c7849294648c1e79dd16077a388b808fcf8c20035aec7cc5315b37dacfee'

    is_paid = 'False'

    class Meta:
        exclude = ['wallet']
        abstract = True


class BtcInvoiceFactory(InvoiceFactory):
    wallet = factory.SubFactory(BtcFactory)

    class Meta:
        model = models.Invoice


class LtcInvoiceFactory(InvoiceFactory):
    wallet = factory.SubFactory(LtcFactory)

    class Meta:
        model = models.Invoice


class DashInvoiceFactory(InvoiceFactory):
    wallet = factory.SubFactory(DashFactory)

    class Meta:
        model = models.Invoice


class DogeInvoiceFactory(InvoiceFactory):
    wallet = factory.SubFactory(DogeFactory)

    class Meta:
        model = models.Invoice


class BcyInvoiceFactory(InvoiceFactory):
    wallet = factory.SubFactory(BcyFactory)

    class Meta:
        model = models.Invoice


class PaymentFactory(factory.django.DjangoModelFactory):

    wallet_id = factory.SelfAttribute('wallet.id')
    wallet_type = factory.LazyAttribute(
        lambda o: ContentType.objects.get_for_model(o.wallet)
    )

    amount = '1'

    class Meta:
        exclude = ['wallet']
        abstract = True


class PaymentBtcInvoiceFactory(PaymentFactory):
    invoice = factory.SubFactory(BtcInvoiceFactory)
    wallet = factory.SubFactory(BtcFactory)

    class Meta:
        model = models.Payment
        exclude = ['wallet']


class PaymentLtcInvoiceFactory(PaymentFactory):
    invoice = factory.SubFactory(LtcInvoiceFactory)
    wallet = factory.SubFactory(LtcFactory)

    class Meta:
        model = models.Payment
        exclude = ['wallet']


class PaymentDashInvoiceFactory(PaymentFactory):
    invoice = factory.SubFactory(DashInvoiceFactory)
    wallet = factory.SubFactory(DashFactory)

    class Meta:
        model = models.Payment
        exclude = ['wallet']


class PaymentDogeInvoiceFactory(PaymentFactory):
    invoice = factory.SubFactory(DogeInvoiceFactory)
    wallet = factory.SubFactory(DogeFactory)

    class Meta:
        model = models.Payment
        exclude = ['wallet']


class PaymentBcyInvoiceFactory(PaymentFactory):
    invoice = factory.SubFactory(BcyInvoiceFactory)
    wallet = factory.SubFactory(BcyFactory)

    class Meta:
        model = models.Payment
        exclude = ['wallet']
