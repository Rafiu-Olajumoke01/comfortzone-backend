from rest_framework import serializers

from .models import PaymentAccount


class PaymentAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentAccount
        fields = ("bank_name", "account_name", "account_number", "note")