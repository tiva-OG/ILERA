from rest_framework import serializers

from .models import CareSession, HealthRecord
from apps.users.models import FarmerProfile, VetProfile


class CareSessionSerializer(serializers.ModelSerializer):
    farmer_name = serializers.CharField(source="farmer.user.get_fullname", read_only=True)
    vet_name = serializers.CharField(source="vet.user.get_fullname", read_only=True)
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = CareSession
        fields = ["id", "farmer", "vet", "status", "created_at", "started_at", "ended_at", "is_active", "farmer_name", "vet_name"]
        read_only_fields = ["created_at", "started_at", "ended_at", "is_active"]


class HealthRecordSerializer(serializers.ModelSerializer):
    livestock_name = serializers.CharField(source="livestock.get_fullname", read_only=True)

    class Meta:
        model = HealthRecord
        fields = ["id", "session", "livestock", "livestock_name", "record_type", "notes", "recorded_at"]
        read_only_fields = ["recorded_at"]
