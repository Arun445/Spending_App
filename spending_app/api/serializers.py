from rest_framework import serializers
from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    # Serializer for trasaction objects
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ('id',)
