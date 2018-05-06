from django.test import TestCase
from .factories import (UserFactory, PaymentBcyInvoiceFactory,
                        BcyFactory, BcyInvoiceFactory,
                        BtcFactory, BtcInvoiceFactory,
                        PaymentBtcInvoiceFactory)
from wallets import queries
from guardian.shortcuts import assign_perm
from random import randint


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

        total = queries.user_total_earned_usd(self.user)
        print(total)
        self.assertNotEqual(total, 0)

    def test_without_payments(self):
        total = queries.user_total_earned_usd(self.user)
        self.assertEqual(total, 0)
