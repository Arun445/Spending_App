from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .models import Transaction, Wallet
from .serializers import TransactionSerializer, WalletSerializer


class TransactionViewSet(viewsets.GenericViewSet,
                         mixins.ListModelMixin,
                         mixins.CreateModelMixin):
    # Manage transactions in the database
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def get_queryset(self):
        # return objects, for the current authenticated user only
        return self.queryset.filter(user=self.request.user).order_by('-date')

    def perform_create(self, serializer):
        # Create a new transaction
        serializer.save(user=self.request.user)


class WalletViewSet(viewsets.GenericViewSet,
                    mixins.ListModelMixin,
                    mixins.CreateModelMixin):
    serializer_class = WalletSerializer
    queryset = Wallet.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        # return all the wallets for the current authenticated user
        return self.queryset.filter(user=self.request.user)\
            .order_by('-balance')

    def perform_create(self, serializer):
        # Create a new wallet
        serializer.save(user=self.request.user)
