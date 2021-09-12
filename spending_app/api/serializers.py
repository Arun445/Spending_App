
from rest_framework import serializers
from .models import Transaction, Wallet, Tag


class WalletSerializer(serializers.ModelSerializer):
    # Serializer for Wallet objects
    class Meta:
        model = Wallet
        fields = '__all__'
        read_only_fields = ('id',)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('id',)


class TransactionSerializer(serializers.ModelSerializer):
    # Serializer for trasaction objects
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ('id',)


class TransactionDetailSerializer(TransactionSerializer):
    # Serialize a transaction detail
    tags = TagSerializer(many=True, read_only=True)


class TransactionImageSerializer(serializers.ModelSerializer):
    # Serializerfor uploading images to recipes

    class Meta:
        model = Transaction
        fields = ('id', 'image')
        read_only_fields = ('id',)
