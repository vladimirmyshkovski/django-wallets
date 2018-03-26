from rest_framework import routers
from .viewsets import BtcViewSet, LtcViewSet, DashViewSet, DogeViewSet, WebhookViewSet#, BcyViewSet
from django.urls import re_path

app_name = 'api_wallets'

router = routers.SimpleRouter()
router.register(r'', WebhookViewSet, base_name='webhook')
router.register(r'btc', BtcViewSet)
router.register(r'ltc', LtcViewSet)
router.register(r'dash', DashViewSet)
router.register(r'doge', DogeViewSet)
#router.register(r'bcy', BcyViewSet)
urlpatterns = router.urls
'''
urlpatterns = [
	re_path(r'^webhook/$', WebhookViewSet),
] + router.urls
'''