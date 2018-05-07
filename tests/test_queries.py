from django.test import TestCase
from .factories import (UserFactory, BtcFactory,
                        BtcInvoiceFactory,
                        PaymentBtcInvoiceFactory)
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
            400
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
            queries.get_user_wallet_balance_usd(self.user, 'btc')>
            400
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
