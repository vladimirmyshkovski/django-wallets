#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_wallets
------------

Tests for `wallets` models module.
"""

from django.test import TestCase

from wallets import models
from wallets import api
from . import factories

import mock

import blockcypher
from guardian.shortcuts import assign_perm


class Response(object):

    def __init__(self):
        super(Response, self).__init__()
        json = {'price_usd': '7072.35'}

        def json(self):
            return self. json

        def override_json(self, json):
            self.json = json
            return json


class TestBtc(TestCase):

    def setUp(self):
        self.btc = factories.BtcFactory()

    def test_btc_data(self):
        self.assertEqual(
            self.btc.coin_symbol,
            'btc'
        )
        self.assertEqual(
            self.btc.coin_name,
            'bitcoin'
        )

    def test_get_absolute_url(self):
        self.assertEqual(
            self.btc.get_absolute_url(),
            '/wallets/btc/{}/_detail/'.format(self.btc.address)
        )

    def test__str__(self):
        self.assertEqual(
            self.btc.__str__(),
            '({}) {}'.format(
                self.btc.coin_symbol.upper(),
                self.btc.address
            )
        )

    def test_get_coin_symbol(self):
        self.assertEqual(
            models.Btc.get_coin_symbol(),
            self.btc.coin_symbol
        )
        self.assertEqual(
            self.btc.coin_symbol,
            'btc'
        )

    def test_get_coin_name(self):
        self.assertEqual(
            models.Btc.get_coin_name(),
            self.btc.coin_name
        )
        self.assertEqual(
            self.btc.coin_name,
            'bitcoin'
        )        
    '''
    def test_get_invoices_without_data(self):
        invoices = self.btc.__class__.get_invoices(
            user=self.btc.user,
            symbol='btc'
        )
        self.assertQuerysetEqual(
            invoices,
            []
        )

    def test_get_invoices_with_data(self):
        invoice = factories.BtcInvoiceFactory(
            wallet=self.btc,
        )
        invoices = self.btc.get_invoices(
            user=self.btc.user,
            symbol='btc'
        )
        self.assertTrue(
            invoice in invoices
        )
        self.assertEqual(
            len(invoices),
            1
        )
        self.assertTrue(
            isinstance(invoices[0], models.Invoice)
        )

    def test_get_payments_without_data(self):
        payments = self.btc.__class__.get_payments(
            user=self.btc.user,
            symbol='btc'
        )
        self.assertQuerysetEqual(
            payments,
            []
        )

    def test_get_payments_with_data(self):
        invoice = factories.BtcInvoiceFactory(
            wallet=self.btc,
        )
        payment = factories.PaymentBtcInvoiceFactory(
            invoice=invoice,
            wallet=self.btc
        )
        payments = self.btc.__class__.get_payments(
            user=self.btc.user,
            symbol='btc'
        )
        self.assertEqual(
            invoice,
            payment.invoice
        )
        self.assertEqual(
            len(payments),
            1
        )
        self.assertTrue(
            payment in payments
        )
        self.assertTrue(
            isinstance(payments[0], models.Payment)
        )

    def test_get_count_unpaid_payments_without_data(self):
        payments = self.btc.__class__.get_count_unpaid_payments(
            user=self.btc.user,
            symbol='btc'
        )
        self.assertEqual(
            payments,
            0
        )

    def test_get_count_unpaid_payments_with_data(self):
        invoice = factories.BtcInvoiceFactory(
            wallet=self.btc,
        )
        factories.PaymentBtcInvoiceFactory(
            invoice=invoice,
            wallet=self.btc
        )
        payments = self.btc.__class__.get_count_unpaid_payments(
            user=self.btc.user,
            symbol='btc'
        )
        self.assertEqual(
            payments,
            1
        )

    def test_get_count_unpaid_invoices_without_data(self):
        invoices = self.btc.__class__.get_count_unpaid_invoices(
            user=self.btc.user,
            symbol='btc'
        )
        self.assertEqual(
            invoices,
            0
        )

    def test_get_count_unpaid_invoices_with_data(self):
        factories.BtcInvoiceFactory(
            wallet=self.btc,
        )
        invoices = self.btc.__class__.get_count_unpaid_invoices(
            user=self.btc.user,
            symbol='btc'
        )
        self.assertEqual(
            invoices,
            1
        )
    '''
    def test_get_rate(self):
        response = Response()
        response = mock.MagicMock(return_value=response)
        self.assertTrue(float(models.Btc.get_rate()) > 0)

    def test_spend(self):
        api.not_simple_spend = mock.MagicMock(
            return_value='d1d5d3a128e354fd699af7eeafb7530279c8a074c4c168bc7d' +
                         '931368c0614893')
        new_transaction = self.btc.spend(
            ['1C1mCxRukix1KfegAY5zQQJV7samAciZpv'],
            [25000]
        )
        self.assertEqual(
            type(new_transaction),
            type('')
        )

    def test_set_webhook(self):
        blockcypher.subscribe_to_address_webhook = mock.MagicMock(
            return_value='bcaf7c39-9a7f-4e8b-8ba4-23b3c1806039'
        )
        signature = mock.MagicMock(
            return_value='asdasdzlkjhwiejhdkchjxkchuxhgkewhrkd'
        )
        webhook = self.btc.set_webhook(
            to_addresses='1HL7fjCRGKC4EfPRjHVgmLmi7Bmpz8hGps',
            transaction='7981c7849294648c1e79dd16077a388b808fcf8c20035aec7cc' +
                        '5315b37dacfee',
            event='confirmed-tx'
        )
        self.assertEqual(
            type(webhook),
            type('')
        )

    def test_spend_with_webhook(self):
        blockcypher.simple_spend = mock.MagicMock(
            return_value='7981c7849294648c1e79dd16077a388b808fcf8c20035aec7c' +
                         'c5315b37dacfee'
        )
        set_webhook = mock.MagicMock(
            return_value='bcaf7c39-9a7f-4e8b-8ba4-23b3c1806039'
        )
        new_transaction = self.btc.spend_with_webhook(
            ['1HL7fjCRGKC4EfPRjHVgmLmi7Bmpz8hGps'],
            [0.25]
        )
        self.assertEqual(
            type(new_transaction),
            type('')
        )
        self.assertEqual(
            type(set_webhook()),
            type('')
        )
    '''
    #def test_rate(self):
    #    response = Response()
    #    response = mock.MagicMock(return_value=response)
    #    rate = self.btc.rate
    #    self.assertTrue(float(rate) > 0)
    '''

    def test_address_details(self):
        blockcypher.get_address_details = mock.MagicMock(
            return_value={
                "address": "1DEP8i3QJCsomS4BSMY2RpU1upv62aGvhD",
                "balance": 4433416,
                "final_balance": 4433416,
                "final_n_tx": 7,
                "n_tx": 7,
                "total_received": 4433416,
                "total_sent": 0,
                "tx_url": "https://api.blockcypher.com/v1/btc/main/txs/",
                "txrefs": [
                    {
                        "block_height": 302013,
                        "confirmations": 77809,
                        "confirmed": "datetime.datetime(2014, 5, 22, 3, 46," +
                                     " 25, 0, tzinfo=tzutc())",
                        "double_spend": False,
                        "ref_balance": 4433416,
                        "spent": False,
                        "tx_hash": "14b1052855bbf6561bc4db8aa501762e7cc1e869" +
                                   "94dda9e782a6b73b1ce0dc1e",
                        "tx_input_n": -1,
                        "tx_output_n": 0,
                        "value": 20213
                    },
                    {
                        "block_height": 302002,
                        "confirmations": 77820,
                        "confirmed": "datetime.datetime(2014, 5, 22, 2, " +
                                     "56, 8, 0, tzinfo=tzutc())",
                        "double_spend": False,
                        "ref_balance": 4413203,
                        "spent": False,
                        "tx_hash": "4cff011ec53022f2ae47197d1a2fd4a6ac2a80" +
                                   "139f4d0131c1fed625ed5dc869",
                        "tx_input_n": -1,
                        "tx_output_n": 0,
                        "value": 40596
                    },
                ],
                "unconfirmed_balance": 0,
                "unconfirmed_n_tx": 0,
                "unconfirmed_txrefs": []
            }
        )
        address_details = self.btc.address_details
        self.assertEqual(
            type(address_details),
            type({})
        )

    def test_overview(self):
        blockcypher.get_address_overview = mock.MagicMock(
            return_value={
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
        overview = self.btc.overview
        self.assertEqual(
            type(overview),
            type({})
        )

    def test_balance(self):
        blockcypher.get_address_overview = mock.MagicMock(
            return_value={
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
            type(self.btc.balance),
            type(1)
        )

    def test_transactions(self):
        self.address_details = mock.MagicMock(
            return_value={
                "address": "1DEP8i3QJCsomS4BSMY2RpU1upv62aGvhD",
                "balance": 4433416,
                "final_balance": 4433416,
                "final_n_tx": 7,
                "n_tx": 7,
                "total_received": 4433416,
                "total_sent": 0,
                "tx_url": "https://api.blockcypher.com/v1/btc/main/txs/",
                "txrefs": [
                    {
                        "block_height": 302013,
                        "confirmations": 77809,
                        "confirmed": "datetime.datetime(2014, 5, 22," +
                                     " 3, 46, 25, 0, tzinfo=tzutc())",
                        "double_spend": False,
                        "ref_balance": 4433416,
                        "spent": False,
                        "tx_hash": "14b1052855bbf6561bc4db8aa501762e7cc" +
                                   "1e86994dda9e782a6b73b1ce0dc1e",
                        "tx_input_n": -1,
                        "tx_output_n": 0,
                        "value": 20213
                    },
                    {
                        "block_height": 302002,
                        "confirmations": 77820,
                        "confirmed": "datetime.datetime(2014, 5, 22, 2," +
                                     " 56, 8, 0, tzinfo=tzutc())",
                        "double_spend": False,
                        "ref_balance": 4413203,
                        "spent": False,
                        "tx_hash": "4cff011ec53022f2ae47197d1a2fd4a6ac2a" +
                                   "80139f4d0131c1fed625ed5dc869",
                        "tx_input_n": -1,
                        "tx_output_n": 0,
                        "value": 40596
                    },
                ],
                "unconfirmed_balance": 0,
                "unconfirmed_n_tx": 0,
                "unconfirmed_txrefs": []
            }
        )
        transactions = self.btc.transactions
        self.assertEqual(
            type(transactions),
            type([])
        )

    def test_transaction_details(self):
        blockcypher.get_transaction_details = mock.MagicMock(
            return_value={
                "addresses": [
                    "13XXaBufpMvqRqLkyDty1AXqueZHVe6iyy",
                    "19YtzZdcfs1V2ZCgyRWo8i2wLT8ND1Tu4L",
                    "1BNiazBzCxJacAKo2yL83Wq1VJ18AYzNHy",
                    "1GbMfYui17L5m6sAy3L3WXAtf1P32bxJXq",
                    "1N2f642sbgCMbNtXFajz9XDACDFnFzdXzV"
                ],
                "block_hash": "0000000000000000c504bdea36e531d8089d324f2d" +
                              "936c86e3274f97f8a44328",
                "block_height": 293000,
                "confirmations": 86918,
                "confirmed": "datetime.datetime(2014, 3, 29, 1, 29, 19," +
                             " 0, tzinfo=tzutc())",
                "double_spend": False,
                "fees": 0,
                "hash": "f854aebae95150b379cc1187d848d58225f3c4157fe992bcd1" +
                        "66f58bd5063449",
                "inputs": [
                    {
                        "addresses": [
                            "1GbMfYui17L5m6sAy3L3WXAtf1P32bxJXq"
                        ],
                        "output_index": 1,
                        "output_value": 16450000,
                        "prev_hash": "583910b7bf90ab802e22e5c25a89b59862b20c" +
                                     "8c1aeb24dfb94e7a508a70f121",
                        "script": "4830450220504b1ccfddf508422bdd8b0fcda2b14" +
                                  "83e87aee1b486c0130bc29226bbce3b4e022100b5" +
                                  "befcfcf0d3bf6ebf0ac2f93badb19e3042c7bed45" +
                                  "6c398e743b885e782466c012103b1feb40b99e8ff" +
                                  "18469484a50e8b52cc478d5f4f773a341fbd920a4" +
                                  "ceaedd4bf",
                        "script_type": "pay-to-pubkey-hash",
                        "sequence": 4294967295
                    },
                ],
                "lock_time": 0,
                "outputs": [
                    {
                        "addresses": [
                            "1N2f642sbgCMbNtXFajz9XDACDFnFzdXzV"
                        ],
                        "script": "76a914e6aad9d712c419ea8febf009a3f3bfdd8d2" +
                                  "22fac88ac",
                        "script_type": "pay-to-pubkey-hash",
                        "spent_by": "35832d6c70b98b54e9a53ab2d51176eb19ad11b" +
                                    "c4505d6bb1ea6c51a68cb92ee",
                        "value": 70320221545
                    }
                ],
                "preference": "low",
                "received": "datetime.datetime(2014, 3, 29, 1, 29, " +
                            "19, 0, tzinfo=tzutc())",
                "relayed_by": "",
                "size": 636,
                "total": 70320221545,
                "ver": 1,
                "vin_sz": 4,
                "vout_sz": 1
            }
        )
        transaction_details = self.btc.transaction_details(
            tx_ref='f854aebae95150b379cc1187d848d58225f3c4157fe992bcd16' +
                   '6f58bd5063449', coin_symbol='btc')
        self.assertEqual(
            type(transaction_details),
            type({})
        )
    '''
    def test_total_balance(self):
        self.assertEqual(
            type(self.btc.total_balance),
            type(1)
        )
    '''
    def test_create_invoice_with_valid_data(self):
        '''
        invoice = self.btc.create_invoice(
            amounts=[100],
            wallets=[self.btc],
        )
        '''
        data = [
            {
                'amount': 100,
                'wallet': self.btc,
                'content_object': self.btc.user,
                'purpose': 'Test payment'
            },
        ]
        invoice = self.btc.create_invoice(
            content_object=self.btc.user,
            data=data
        )
        btc = models.Btc.objects.get(pk=self.btc.pk)
        self.assertTrue(isinstance(invoice, models.Invoice))
        self.assertEqual(invoice.amount, 100)
        self.assertEqual(btc.invoices.first(), invoice)
        self.assertEqual(
            btc.payments.first(),
            invoice.payments.first()
        )

    def test_create_invoice_with_invalid_data(self):
        #btc = factories.BtcFactory()
        #invoice = self.btc.create_invoice(
        #    amounts=[100, 25],
        #    wallets=[btc],
        #)
        '''
        data = [
            {
                'amount': 100,
                'wallet': self.btc,
                'content_object': self.btc.user,
                'purpose': 'Test payment'
            },
            {
                'amount': ,
                'wallet': self.btc,
                'content_object': self.btc.user,
                'purpose': 'Test payment'
            }
        ]
        self.assertRaises(
            AssertionError,
            lambda: self.btc.create_invoice(
                content_object=self.btc.user, data=data
            )
        )
        '''
        #self.assertTrue(isinstance(invoice, models.Invoice))
        #self.assertEqual(invoice.amount, 100)
        #self.assertTrue(btc in invoice.receiver_wallet_object.all())
        #self.assertEqual(btc.invoice_set.first(), invoice)
        pass

    def tearDown(self):
        pass


class TestLtc(TestCase):

    def setUp(self):
        self.ltc = factories.LtcFactory()

    def test_btc_data(self):
        self.assertEqual(
            self.ltc.coin_symbol,
            'ltc'
        )
        self.assertEqual(
            self.ltc.coin_name,
            'litecoin'
        )

    def test_get_absolute_url(self):
        self.assertEqual(
            self.ltc.get_absolute_url(),
            '/wallets/ltc/{}/_detail/'.format(self.ltc.address)
        )

    def test__str__(self):
        self.assertEqual(
            self.ltc.__str__(),
            '({}) {}'.format(
                self.ltc.coin_symbol.upper(),
                self.ltc.address
            )
        )

    def test_overview(self):
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
        overview = self.ltc.overview
        self.assertEqual(
            type(overview),
            type({})
        )

    def test_balance(self):
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
        balance = self.ltc.balance
        self.assertEqual(
            type(balance),
            type(1)
        )
    '''
    def test_total_balance(self):
        self.assertEqual(
            type(self.ltc.total_balance),
            type(1)
        )
    '''


class TestDash(TestCase):

    def setUp(self):
        self.dash = factories.DashFactory()

    def test_btc_data(self):
        self.assertEqual(
            self.dash.coin_symbol,
            'dash'
        )
        self.assertEqual(
            self.dash.coin_name,
            'dash'
        )

    def test_get_absolute_url(self):
        self.assertEqual(
            self.dash.get_absolute_url(),
            '/wallets/dash/{}/_detail/'.format(self.dash.address)
        )

    def test__str__(self):
        self.assertEqual(
            self.dash.__str__(),
            '({}) {}'.format(
                self.dash.coin_symbol.upper(),
                self.dash.address
            )
        )

    def test_overview(self):
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
        overview = self.dash.overview
        self.assertEqual(
            type(overview),
            type({})
        )

    def test_balance(self):
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
        balance = self.dash.balance
        self.assertEqual(
            type(balance),
            type(1)
        )
    '''
    def test_total_balance(self):
        self.assertEqual(
            type(self.dash.total_balance),
            type(1)
        )
    '''


class TestDoge(TestCase):

    def setUp(self):
        self.doge = factories.DogeFactory()

    def test_btc_data(self):
        self.assertEqual(
            self.doge.coin_symbol,
            'doge'
        )
        self.assertEqual(
            self.doge.coin_name,
            'dogecoin'
        )

    def test_get_absolute_url(self):
        self.assertEqual(
            self.doge.get_absolute_url(),
            '/wallets/doge/{}/_detail/'.format(self.doge.address)
        )

    def test__str__(self):
        self.assertEqual(
            self.doge.__str__(),
            '({}) {}'.format(
                self.doge.coin_symbol.upper(),
                self.doge.address
            )
        )

    def test_overview(self):
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
        overview = self.doge.overview
        self.assertEqual(
            type(overview),
            type({})
        )

    def test_balance(self):
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
        balance = self.doge.balance
        self.assertEqual(
            type(balance),
            type(1)
        )
    '''
    def test_total_balance(self):
        self.assertEqual(
            type(self.doge.total_balance),
            type(1)
        )
    '''


class TestBcy(TestCase):

    def setUp(self):
        self.user = factories.UserFactory()
        self.bcy = factories.BcyFactory(user=self.user)

    def test_btc_data(self):
        self.assertEqual(
            self.bcy.coin_symbol,
            'bcy'
        )
        self.assertEqual(
            self.bcy.coin_name,
            'blockcypher'
        )

    def test_get_absolute_url(self):
        self.assertEqual(
            self.bcy.get_absolute_url(),
            '/wallets/bcy/{}/_detail/'.format(self.bcy.address)
        )

    def test__str__(self):
        self.assertEqual(
            self.bcy.__str__(),
            '(BCY) {}'.format(self.bcy.address)
        )

    def test_overview(self):
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
        overview = self.bcy.overview
        self.assertEqual(
            type(overview),
            type({})
        )

    def test_balance(self):

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
        balance = self.bcy.balance
        self.assertEqual(
            type(balance),
            type(1)
        )
    '''
    def test_total_balance(self):
        self.assertEqual(
            type(self.bcy.total_balance),
            type(1)
        )
    '''
    #def test_rate(self):
    #    rate = self.bcy.rate
    #    self.assertEqual(rate, 150)


class TestInvoice(TestCase):

    def setUp(self):
        self.btc_invoice = factories.BtcInvoiceFactory()
        self.ltc_invoice = factories.LtcInvoiceFactory()
        self.dash_invoice = factories.DashInvoiceFactory()
        self.doge_invoice = factories.DogeInvoiceFactory()
        assign_perm(
            'view_invoice',
            self.btc_invoice.wallet.user,
            self.btc_invoice
        )
        assign_perm(
            'pay_invoice',
            self.btc_invoice.wallet.user,
            self.btc_invoice
        )

        assign_perm(
            'view_invoice',
            self.ltc_invoice.wallet.user,
            self.ltc_invoice
        )
        assign_perm(
            'pay_invoice',
            self.ltc_invoice.wallet.user,
            self.ltc_invoice
        )

        assign_perm(
            'view_invoice',
            self.dash_invoice.wallet.user,
            self.dash_invoice
        )
        assign_perm(
            'pay_invoice',
            self.dash_invoice.wallet.user,
            self.dash_invoice
        )

        assign_perm(
            'view_invoice',
            self.doge_invoice.wallet.user,
            self.doge_invoice
        )
        assign_perm(
            'pay_invoice',
            self.doge_invoice.wallet.user,
            self.doge_invoice
        )

    def test_get_absolute_url(self):
        self.assertEqual(
            self.btc_invoice.get_absolute_url(),
            '/wallets/invoices/{}/_detail/'.format(self.btc_invoice.pk)
        )
        self.assertEqual(
            self.ltc_invoice.get_absolute_url(),
            '/wallets/invoices/{}/_detail/'.format(self.ltc_invoice.pk)
        )
        self.assertEqual(
            self.dash_invoice.get_absolute_url(),
            '/wallets/invoices/{}/_detail/'.format(self.dash_invoice.pk)
        )
        self.assertEqual(
            self.doge_invoice.get_absolute_url(),
            '/wallets/invoices/{}/_detail/'.format(self.doge_invoice.pk)
        )

    def test_has_no_changed(self):
        blockcypher.get_transaction_details = mock.MagicMock(
            return_value={
                "addresses": [
                    "13XXaBufpMvqRqLkyDty1AXqueZHVe6iyy",
                    "19YtzZdcfs1V2ZCgyRWo8i2wLT8ND1Tu4L",
                    "1BNiazBzCxJacAKo2yL83Wq1VJ18AYzNHy",
                    "1GbMfYui17L5m6sAy3L3WXAtf1P32bxJXq",
                    "1N2f642sbgCMbNtXFajz9XDACDFnFzdXzV"
                ],
                "block_hash": "0000000000000000c504bdea36e531d8089d324f2d" +
                              "936c86e3274f97f8a44328",
                "block_height": 293000,
                "confirmations": 86918,
                "confirmed": "datetime.datetime(2014, 3, 29, 1, 29, 19," +
                             " 0, tzinfo=tzutc())",
                "double_spend": False,
                "fees": 0,
                "hash": "f854aebae95150b379cc1187d848d58225f3c4157fe992bcd1" +
                        "66f58bd5063449",
                "inputs": [
                    {
                        "addresses": [
                            "1GbMfYui17L5m6sAy3L3WXAtf1P32bxJXq"
                        ],
                        "output_index": 1,
                        "output_value": 16450000,
                        "prev_hash": "583910b7bf90ab802e22e5c25a89b59862b20c" +
                                     "8c1aeb24dfb94e7a508a70f121",
                        "script": "4830450220504b1ccfddf508422bdd8b0fcda2b14" +
                                  "83e87aee1b486c0130bc29226bbce3b4e022100b5" +
                                  "befcfcf0d3bf6ebf0ac2f93badb19e3042c7bed45" +
                                  "6c398e743b885e782466c012103b1feb40b99e8ff" +
                                  "18469484a50e8b52cc478d5f4f773a341fbd920a4" +
                                  "ceaedd4bf",
                        "script_type": "pay-to-pubkey-hash",
                        "sequence": 4294967295
                    },
                ],
                "lock_time": 0,
                "outputs": [
                    {
                        "addresses": [
                            "1N2f642sbgCMbNtXFajz9XDACDFnFzdXzV"
                        ],
                        "script": "76a914e6aad9d712c419ea8febf009a3f3bfdd8d2" +
                                  "22fac88ac",
                        "script_type": "pay-to-pubkey-hash",
                        "spent_by": "35832d6c70b98b54e9a53ab2d51176eb19ad11b" +
                                    "c4505d6bb1ea6c51a68cb92ee",
                        "value": 70320221545
                    }
                ],
                "preference": "low",
                "received": "datetime.datetime(2014, 3, 29, 1, 29, " +
                            "19, 0, tzinfo=tzutc())",
                "relayed_by": "",
                "size": 636,
                "total": 70320221545,
                "ver": 1,
                "vin_sz": 4,
                "vout_sz": 1
            }
        )
        self.btc_invoice.is_paid = True
        factories.PaymentBtcInvoiceFactory(invoice=self.btc_invoice, amount=1)
        self.btc_invoice.save()
        self.assertFalse(self.btc_invoice.is_paid)
        self.assertEqual(self.btc_invoice.amount, 1)

    def test_has_changed(self):
        blockcypher.get_transaction_details = mock.MagicMock(
            return_value={
                "addresses": [
                    "13XXaBufpMvqRqLkyDty1AXqueZHVe6iyy",
                    "19YtzZdcfs1V2ZCgyRWo8i2wLT8ND1Tu4L",
                    "1BNiazBzCxJacAKo2yL83Wq1VJ18AYzNHy",
                    "1GbMfYui17L5m6sAy3L3WXAtf1P32bxJXq",
                    "1N2f642sbgCMbNtXFajz9XDACDFnFzdXzV"
                ],
                "block_hash": "0000000000000000c504bdea36e531d8089d324f2d" +
                              "936c86e3274f97f8a44328",
                "block_height": 293000,
                "confirmations": 86918,
                "confirmed": "datetime.datetime(2014, 3, 29, 1, 29, 19," +
                             " 0, tzinfo=tzutc())",
                "double_spend": False,
                "fees": 0,
                "hash": "f854aebae95150b379cc1187d848d58225f3c4157fe992bcd1" +
                        "66f58bd5063449",
                "inputs": [
                    {
                        "addresses": [
                            "1GbMfYui17L5m6sAy3L3WXAtf1P32bxJXq"
                        ],
                        "output_index": 1,
                        "output_value": 16450000,
                        "prev_hash": "583910b7bf90ab802e22e5c25a89b59862b20c" +
                                     "8c1aeb24dfb94e7a508a70f121",
                        "script": "4830450220504b1ccfddf508422bdd8b0fcda2b14" +
                                  "83e87aee1b486c0130bc29226bbce3b4e022100b5" +
                                  "befcfcf0d3bf6ebf0ac2f93badb19e3042c7bed45" +
                                  "6c398e743b885e782466c012103b1feb40b99e8ff" +
                                  "18469484a50e8b52cc478d5f4f773a341fbd920a4" +
                                  "ceaedd4bf",
                        "script_type": "pay-to-pubkey-hash",
                        "sequence": 4294967295
                    },
                ],
                "lock_time": 0,
                "outputs": [
                    {
                        "addresses": [
                            "1N2f642sbgCMbNtXFajz9XDACDFnFzdXzV"
                        ],
                        "script": "76a914e6aad9d712c419ea8febf009a3f3bfdd8d2" +
                                  "22fac88ac",
                        "script_type": "pay-to-pubkey-hash",
                        "spent_by": "35832d6c70b98b54e9a53ab2d51176eb19ad11b" +
                                    "c4505d6bb1ea6c51a68cb92ee",
                        "value": 70320221545
                    }
                ],
                "preference": "low",
                "received": "datetime.datetime(2014, 3, 29, 1, 29, " +
                            "19, 0, tzinfo=tzutc())",
                "relayed_by": "",
                "size": 636,
                "total": 70320221545,
                "ver": 1,
                "vin_sz": 4,
                "vout_sz": 1
            }
        )
        factories.PaymentBtcInvoiceFactory(
            invoice=self.btc_invoice,
            amount=703202215451
        )
        #self.btc_invoice.tx_ref = '4cff011ec53022f2ae47197d1a2fd4a6ac2a80139f4d0131c1fed625ed5dc869'
        #self.btc_invoice.save()
        #self.invoice_transaction = factories.InvoiceTransactionFactory(
        #    invoice=self.btc_invoice,
        #    tx_ref='4cff011ec53022f2ae47197d1a2fd4a6ac2a80139f4d0131c1f' +
        #           'ed625ed5dc869'
        #)

        self.btc_invoice.is_paid = True
        self.assertTrue(self.btc_invoice.has_changed())
        self.btc_invoice.save()
        self.assertTrue(self.btc_invoice.is_paid)
        self.btc_invoice.is_paid = False
        self.btc_invoice.save()
        self.assertFalse(self.btc_invoice.is_paid)
        self.btc_invoice.is_paid = True
        self.btc_invoice.save()
        self.assertTrue(self.btc_invoice.is_paid)

    def test_values(self):
        #self.btc_invoice.amount = [1]
        self.btc_invoice.save()
        values = self.btc_invoice.reset_original_values()
        self.assertEqual(values, {'is_paid': False})

    def test_pay(self):
        api.not_simple_spend = mock.MagicMock(
            return_value='7981c7849294648c1e79dd16077a388b808fcf8c20035aec7' +
                         'cc5315b37dacfee')

        tx_ref = self.btc_invoice.pay()
        self.assertEqual(
            tx_ref,
            '7981c7849294648c1e79dd16077a388b808fcf8c20035aec7cc5315b37dacfee'
        )
        self.assertEqual(
            self.btc_invoice.tx_ref,
            tx_ref
        )
        '''
        invoice_transaction = models.InvoiceTransaction.objects.first()
        self.assertNotEqual(
            invoice_transaction,
            None
        )
        self.assertEqual(
            invoice_transaction.invoice,
            self.btc_invoice
        )
        self.assertEqual(
            invoice_transaction.tx_ref,
            '7981c7849294648c1e79dd16077a388b808fcf8c20035aec7cc5315b37dacfee'
        )
        '''
    '''
    def test_can_be_confirmed(self):

        invoice_transaction = factories.InvoiceTransactionFactory(invoice = self.btc_invoice)
        blockcypher.get_transaction_details = mock.MagicMock(return_value={
                "addresses": [
                    "13XXaBufpMvqRqLkyDty1AXqueZHVe6iyy", 
                    "19YtzZdcfs1V2ZCgyRWo8i2wLT8ND1Tu4L", 
                    "1BNiazBzCxJacAKo2yL83Wq1VJ18AYzNHy", 
                    "1GbMfYui17L5m6sAy3L3WXAtf1P32bxJXq", 
                    "1N2f642sbgCMbNtXFajz9XDACDFnFzdXzV"
                ], 
                "block_hash": "0000000000000000c504bdea36e531d8089d324f2d936c86e3274f97f8a44328", 
                "block_height": 293000, 
                "confirmations": 86918, 
                "confirmed": "datetime.datetime(2014, 3, 29, 1, 29, 19, 0, tzinfo=tzutc())", 
                "double_spend": False, 
                "fees": 0, 
                "hash": "f854aebae95150b379cc1187d848d58225f3c4157fe992bcd166f58bd5063449", 
                "inputs": [
                    {
                        "addresses": [
                            "1GbMfYui17L5m6sAy3L3WXAtf1P32bxJXq"
                        ], 
                        "output_index": 1, 
                        "output_value": 16450000, 
                        "prev_hash": "583910b7bf90ab802e22e5c25a89b59862b20c8c1aeb24dfb94e7a508a70f121", 
                        "script": "4830450220504b1ccfddf508422bdd8b0fcda2b1483e87aee1b486c0130bc29226bbce3b4e022100b5befcfcf0d3bf6ebf0ac2f93badb19e3042c7bed456c398e743b885e782466c012103b1feb40b99e8ff18469484a50e8b52cc478d5f4f773a341fbd920a4ceaedd4bf", 
                        "script_type": "pay-to-pubkey-hash", 
                        "sequence": 4294967295
                    }, 
                ], 
                "lock_time": 0, 
                "outputs": [
                    {
                        "addresses": [
                            "1N2f642sbgCMbNtXFajz9XDACDFnFzdXzV"
                        ], 
                        "script": "76a914e6aad9d712c419ea8febf009a3f3bfdd8d222fac88ac", 
                        "script_type": "pay-to-pubkey-hash", 
                        "spent_by": "35832d6c70b98b54e9a53ab2d51176eb19ad11bc4505d6bb1ea6c51a68cb92ee", 
                        "value": 70320221545
                    }
                ], 
                "preference": "low", 
                "received": "datetime.datetime(2014, 3, 29, 1, 29, 19, 0, tzinfo=tzutc())", 
                "relayed_by": "", 
                "size": 636, 
                "total": 70320221545, 
                "ver": 1, 
                "vin_sz": 4, 
                "vout_sz": 1
            }
        )
        can_be_confirmed = self.btc_invoice.can_be_confirmed()
        '''

'''
class TestInvoiceTransaction(TestCase):

    def setUp(self):
        self.invoice_transaction = factories.InvoiceTransactionFactory()

    def test__str__(self):
        self.assertEqual(
            self.invoice_transaction.__str__(),
            '4cff011ec53022f2ae47197d1a2fd4a6ac2a80139f4d0131c1fed625ed5dc869'
        )
'''