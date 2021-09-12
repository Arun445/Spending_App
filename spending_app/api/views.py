from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .models import Tag, Transaction, Wallet
from .serializers import (TransactionImageSerializer, TransactionSerializer,
                          WalletSerializer, TagSerializer,
                          TransactionDetailSerializer)


class BaseSpendingProfileAttrViewSet(viewsets.GenericViewSet,
                                     mixins.ListModelMixin,
                                     mixins.CreateModelMixin):
    # Base viewset for spending app user profile attributes
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        # Create a new object
        serializer.save(user=self.request.user)


class WalletViewSet(BaseSpendingProfileAttrViewSet):
    # Manage wallets in the database
    serializer_class = WalletSerializer
    queryset = Wallet.objects.all()

    def get_queryset(self):
        # return all the wallets for the current authenticated user
        return self.queryset.filter(user=self.request.user)\
            .order_by('-balance')


class TagViewSet(BaseSpendingProfileAttrViewSet):
    # Manage tags in the database
    serializer_class = TagSerializer
    queryset = Tag.objects.all()

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class TransactionViewSet(viewsets.ModelViewSet):
    # Manage transactions in the database
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def get_queryset(self):
        # return objects, for the current authenticated user only
        return self.queryset.filter(user=self.request.user).order_by('-date')

    def get_serializer_class(self):
        # return appropriate serializer class
        if self.action == 'retrieve':
            return TransactionDetailSerializer
        elif self.action == 'upload_image':
            return TransactionImageSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        # upload an image to a transaction
        transaction = self.get_object()
        serializer = self.get_serializer(
            transaction,
            data=request.data
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
