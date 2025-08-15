# media_gallery/serializers.py
from rest_framework import serializers
from .models import MediaFile

class MediaFileSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.StringRelatedField(read_only=True)
    tour = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = MediaFile
        fields = ['id', 'tour', 'uploaded_by', 'file', 'caption', 'uploaded_at']