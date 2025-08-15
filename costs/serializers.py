# costs/serializers.py

from rest_framework import serializers
from .models import CostEntry

class CostEntrySerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    tour = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = CostEntry
        fields = ['id', 'user', 'tour', 'amount', 'description', 'date']