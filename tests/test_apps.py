from django.apps import apps
from django.test import TestCase
from wallets import apps as wallets_apps


class ReferralsConfigTest(TestCase):

    def test_apps(self):
        self.assertEqual(wallets_apps.WalletsConfig.name, 'wallets')
        self.assertEqual(apps.get_app_config('wallets').name, 'wallets')
