from rest_framework import viewsets, status
from rest_framework.response import Response
from authtoken.permissions import HasTokenScope

from foobar import api
from ..serializers.purchase import (
    PurchaseRequestSerializer,
    PurchaseSerializer,
    PurchaseListSerializer
)
from wallet.exceptions import InsufficientFunds


class PurchaseAPI(viewsets.ViewSet):
    permission_classes = (HasTokenScope('purchases'),)

    def create(self, request):
        serializer = PurchaseRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            purchase_obj = api.purchase(**serializer.as_purchase_kwargs())
        except InsufficientFunds:
            return Response(
                'Insufficient funds',
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = PurchaseSerializer(purchase_obj)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def list(self, request):
        serializer = PurchaseListSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        transaction_objs = api.list_purchases(serializer.validated_data['account_id'])
        purchase_objs = [purchase for purchase, _ in transaction_objs] 
        serializer = PurchaseListSerializer(purchase_objs, many=True)
        return Response(serializer.data)


    def retrieve(self, request, pk):
        purchase_obj, _ = api.get_purchase(pk)
        if purchase_obj is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = PurchaseListSerializer(purchase_obj)        
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )


    def destroy(self, request, pk):
        api.cancel_purchase(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)
