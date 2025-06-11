from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "type",
            "title",
            "body",
            "is_read",
            "metadata",
            "created_at",
            "actor",
            "receiver",
        ]
        read_only_fields = ["id", "created_at", "actor", "receiver"]
