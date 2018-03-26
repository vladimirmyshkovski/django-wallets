from .models import Btc, Ltc, Dash, Doge#, Bcy
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response

from .serializers import BtcSerializer, LtcSerializer, DashSerializer, DogeSerializer, WithdrawSerializer#, BcySerializer
from .permissions import IsOwnerOrReadOnly

from rest_framework import mixins
from rest_framework.decorators import detail_route, list_route

from .utils import decode_signin, extract_webhook_id, unsubscribe_from_webhook
from .validators import withdraw_schema
from cerberus import Validator


from rest_framework.permissions import IsAuthenticated

v = Validator()


class WebhookViewSet(viewsets.ViewSet):

    @detail_route (methods=['post'])
    def webhook(self, request, signature=None):
        #signature = request.data.get('signature', None)
        if not signature:
            content = {"signature": ["This field may not be blank."]}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        sign = decode_signin(signature)
        if sign:
            get_webhook.send(
                sender=None,
                from_address = sign['from_address'],
                to_address = sign['to_address'],
                symbol = sign['symbol'],
                event = sign['event'],
                transaction_id = sign['transaction_id']
                )
            webhook_id = extract_webhook_id(signature, sign['symbol'])
            if webhook_id:
                unsubscribe = unsubscribe_from_webhook(webhook_id)
        return Response(status=status.HTTP_200_OK)


class BaseViewSet(mixins.CreateModelMixin,
                mixins.ListModelMixin,
                mixins.RetrieveModelMixin,
                viewsets.GenericViewSet):

    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def create(self, validated_data):
        instance = self.model.objects.create(user=self.request.user)
        serializer = self.get_serializer(instance)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @detail_route(methods=['post'])
    def withdraw(self, request, pk=None):
        serializer = WithdrawSerializer(request.data)
        if serializer.is_valid():
            try:
                obj = self.get_object()
                
                address = request.data['address']
                amount = request.data['amount']            
                
                transaction = obj.spend(address, float(amount))
                
                #content = 'Transaction {} successfully created'.foramt(transaction)
                
                return Response(serializer.data, status=status.HTTP_200_OK)
            except:
                pass
        return Response({'status': 'Something wrong, try again later'}, status=status.HTTP_400_BAD_REQUEST)

        '''
        if not v.validate(request.data, withdraw_schema):
            return Response(v.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            obj = self.get_object()
            
            address = request.data['address']
            amount = request.data['amount']            
            
            transaction = obj.spend(address, float(amount))
            
            content = 'Transaction {} successfully created'.foramt(transaction)
        except:
            return Response('Something wrong, try again later', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(content, status=status.HTTP_201_CREATED)
        '''

    @list_route(methods=['post'])
    def webhook(self, request):
        signature = request.data.get('signature', None)
        if not signature:
            content = {"signature": ["This field may not be blank."]}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        sign = decode_signin(signature)
        if sign:
            get_webhook.send(
                sender=None,
                from_address = sign['from_address'],
                to_address = sign['to_address'],
                symbol = sign['symbol'],
                event = sign['event'],
                transaction_id = sign['transaction_id']
                )
            webhook_id = extract_webhook_id(signature, sign['symbol'])
            if webhook_id:
                unsubscribe = unsubscribe_from_webhook(webhook_id)
        return Response(status=status.HTTP_200_OK)    


class BtcViewSet(BaseViewSet):
    """
    A simple ViewSet for listing or retrieving Bitcocins addresses.
    """
    serializer_class = BtcSerializer
    queryset = Btc.objects.all()
    permissions = [IsOwnerOrReadOnly]
    model = Btc


class LtcViewSet(BaseViewSet):
    """
    A simple ViewSet for listing or retrieving Litecoins addresses.
    """
    serializer_class = LtcSerializer
    queryset = Ltc.objects.all()
    permissions = [IsOwnerOrReadOnly]
    model = Ltc  


class DashViewSet(BaseViewSet):
    """
    A simple ViewSet for listing or retrieving Dash addresses.
    """
    serializer_class = DashSerializer
    queryset = Dash.objects.all()
    permissions = [IsOwnerOrReadOnly]
    model = Dash


class DogeViewSet(BaseViewSet):
    """
    A simple ViewSet for listing or retrieving Dogecoins addresses.
    """
    serializer_class = DogeSerializer
    queryset = Doge.objects.all()
    permissions = [IsOwnerOrReadOnly]    
    model = Doge

'''
class BcyViewSet(BaseViewSet):
    """
    A simple ViewSet for listing or retrieving Bitcocins testnet addresses.
    """
    serializer_class = BcySerializer
    queryset = Bcy.objects.all()
    permissions = [IsOwnerOrReadOnly]    
    model = Bcy
'''