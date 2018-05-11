from django.test import TestCase
from .factories import (UserFactory, BtcFactory,
                        LtcFactory, BtcInvoiceFactory,
                        LtcInvoiceFactory,
                        PaymentBtcInvoiceFactory,
                        PaymentLtcInvoiceFactory)
from wallets import queries
from guardian.shortcuts import assign_perm
from random import randint
import mock
import blockcypher
'''
class TestUserTotalEarned(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.bcy = BcyFactory(user=self.user)
        self.invoice = BcyInvoiceFactory(wallet=self.bcy, is_paid=True)

    def test_with_payments(self):
        for i in range(10):
            payment = PaymentBcyInvoiceFactory(
                invoice=self.invoice,
                wallet=self.bcy,
                amount=randint(1, 1000)
            )
            assign_perm('view_payment', self.user, payment)

        total = queries.user_total_earned(self.user)
        self.assertNotEqual(total, 0)

    def test_without_payments(self):
        total = queries.user_total_earned(self.user)
        self.assertEqual(total, 0)
'''


class TestUserTotalEarnedUsd(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.btc = BtcFactory(user=self.user)
        self.invoice = BtcInvoiceFactory(wallet=self.btc, is_paid=True)

    def test_with_payments(self):
        for i in range(10):
            payment = PaymentBtcInvoiceFactory(
                invoice=self.invoice,
                wallet=self.btc,
                amount=randint(1, 1000)
            )
            assign_perm('view_payment', self.user, payment)

        total = queries.get_user_total_earned_usd(self.user)
        self.assertNotEqual(total, 0)

    def test_without_payments(self):
        total = queries.get_user_total_earned_usd(self.user)
        self.assertEqual(total, 0)


class TestGetUserTotalBalanceUsd(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.btc = BtcFactory(user=self.user)

    def test(self):
        blockcypher.get_address_overview = mock.MagicMock(return_value={
            "address": "1DEP8i3QJCsomS4BSMY2RpU1upv62aGvhD",
            "balance": 4433416,
            "final_balance": 4433416,
            "final_n_tx": 7,
            "n_tx": 7,
            "total_received": 4433416,
            "total_sent": 0,
            "unconfirmed_balance": 0,
            "unconfirmed_n_tx": 0
        }
        )
        self.assertTrue(
            queries.get_user_total_balance_usd(self.user) >
            300
        )


class TestGetUserWalletBalanceUsd(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.btc = BtcFactory(user=self.user)

    def test(self):
        blockcypher.get_address_overview = mock.MagicMock(return_value={
            "address": "1DEP8i3QJCsomS4BSMY2RpU1upv62aGvhD",
            "balance": 4433416,
            "final_balance": 4433416,
            "final_n_tx": 7,
            "n_tx": 7,
            "total_received": 4433416,
            "total_sent": 0,
            "unconfirmed_balance": 0,
            "unconfirmed_n_tx": 0
        }
        )
        self.assertTrue(
            queries.get_user_wallet_balance_usd(self.user, 'btc') >
            300
        )


class TestGetUserWalletBalance(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.btc = BtcFactory(user=self.user)

    def test(self):
        blockcypher.get_address_overview = mock.MagicMock(return_value={
            "address": "1DEP8i3QJCsomS4BSMY2RpU1upv62aGvhD",
            "balance": 4433416,
            "final_balance": 4433416,
            "final_n_tx": 7,
            "n_tx": 7,
            "total_received": 4433416,
            "total_sent": 0,
            "unconfirmed_balance": 0,
            "unconfirmed_n_tx": 0
        }
        )
        self.assertEqual(
            queries.get_user_wallet_balance(self.user, 'btc'),
            0.04433416
        )


class TestGetAggregateInvoices(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.btc = BtcFactory(user=self.user)
        self.ltc = LtcFactory(user=self.user)

    def test_with_values(self):
        self.btc_invoice = BtcInvoiceFactory(
            wallet=self.btc, content_object=self.user
        )
        self.ltc_invoice = LtcInvoiceFactory(
            wallet=self.ltc, content_object=self.user
        )
        self.btc_payment_one = PaymentBtcInvoiceFactory(
            invoice=self.btc_invoice, content_object=self.user,
            wallet=self.btc, amount=100000000
        )
        self.btc_payment_two = PaymentBtcInvoiceFactory(
            invoice=self.btc_invoice, content_object=self.user,
            wallet=self.btc, amount=100000000
        )
        self.ltc_payment = PaymentLtcInvoiceFactory(
            invoice=self.ltc_invoice, content_object=self.user,
            wallet=self.ltc, amount=100000000
        )
        values = queries.get_aggregate_invoices(self.user)
        self.assertTrue(type(values) is dict)
        for item in values:
            self.assertEqual(
                item,
                self.ltc_payment.modified.strftime('%d.%m.%Y')
            )
            self.assertTrue(values[item] > 0)

    def test_without_values(self):
        values = queries.get_aggregate_invoices(self.user)
        self.assertTrue(type(values) is dict)
