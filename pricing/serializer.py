# pricing/serializers.py
from rest_framework import serializers
from .models import Alert

class PriceAlertSerializer(serializers.Serializer):
    
    price = serializers.DecimalField(max_digits=10, decimal_places=2)


class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = ['id', 'email', 'price', 'status']
        read_only_fields = ['id', 'status']