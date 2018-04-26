from test_plus.test import TestCase
from . import factories
from django.test import RequestFactory
import random
from django.template import Context, Template


class TestUnpaidUserSendedInvoices(TestCase):

    def setUp(self):
        self.user = self.make_user('user-{}'.format(random.randint(1, 100)))

    def test_without_invoices(self):
        request_factory = RequestFactory()
        request = request_factory.get('/')
        request.user = self.user

        out = Template(
            "{% load wallets_tags %}"
            "{% unpaid_user_sended_invoices %}"
        ).render(Context({
            'request': request,
            'symbol': 'bcy'
            }
        ))

        print(out)
