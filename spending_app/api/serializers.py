
from rest_framework import serializers
from .models import Transaction, Wallet


class TransactionSerializer(serializers.ModelSerializer):
    # Serializer for trasaction objects
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ('id',)


class WalletSerializer(serializers.ModelSerializer):
    # Serializer for Wallet objects
    class Meta:
        model = Wallet
        fields = '__all__'
        read_only_fields = ('id',)
