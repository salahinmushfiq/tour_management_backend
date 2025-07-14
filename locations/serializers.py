from rest_framework import serializers
from .models import VisitedRegion


class VisitedRegionSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    tour = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = VisitedRegion
        fields = ['id', 'user', 'tour', 'region_name', 'latitude', 'longitude', 'visited_on']
