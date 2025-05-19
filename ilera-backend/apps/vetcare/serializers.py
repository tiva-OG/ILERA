from rest_framework import serializers

from .models import CareSession, HealthRecord, SessionStatus
from apps.users.models import FarmerProfile, VetProfile


class CareSessionSerializer(serializers.ModelSerializer):
    farmer_name = serializers.CharField(source="farmer.user.get_fullname", read_only=True)
    vet_name = serializers.CharField(source="vet.user.get_fullname", read_only=True)
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = CareSession
        fields = ["id", "vet", "status", "created_at", "started_at", "ended_at", "is_active", "farmer_name", "vet_name"]
        read_only_fields = ["status", "created_at", "started_at", "ended_at", "is_active", "farmer_name", "vet_name"]

    def create(self, validated_data):
        request = self.context["request"]
        farmer_profile = request.user.farmer_profile
        vet_profile = validated_data["vet"]

        if CareSession.objects.filter(farmer=farmer_profile, vet=vet_profile, status__in=[SessionStatus.PENDING, SessionStatus.ACCEPTED]).exists():
            raise serializers.ValidationError("A pending or an ongoing session already exists with this vet.")

        return CareSession.objects.create(farmer=farmer_profile, vet=vet_profile)


class VetSessionSerializer(serializers.ModelSerializer):
    farmer = serializers.SerializerMethodField()
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = CareSession
        fields = ["id", "farmer", "status", "created_at", "started_at", "ended_at", "is_active"]

    def get_farmer(self, obj):
        farmer_user = obj.farmer.user
        return {
            "id": farmer_user.id,
            "name": farmer_user.get_fullname(),
            "phone": farmer_user.phone,
            "email": farmer_user.email,
            "location": obj.farmer.location,
            "bio": obj.farmer.bio,
        }


class FarmerSessionSerializer(serializers.ModelSerializer):
    vet = serializers.SerializerMethodField()
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = CareSession
        fields = ["id", "vet", "status", "created_at", "started_at", "ended_at", "is_active"]

    def get_vet(self, obj):
        vet_user = obj.vet.user
        return {
            "id": vet_user.id,
            "name": vet_user.get_fullname(),
            "phone": vet_user.phone,
            "email": vet_user.email,
            "location": obj.vet.location,
            "bio": obj.vet.bio,
        }


class HealthRecordSerializer(serializers.ModelSerializer):
    livestock_name = serializers.CharField(source="livestock.get_fullname", read_only=True)

    class Meta:
        model = HealthRecord
        fields = ["id", "session", "livestock", "livestock_name", "record_type", "notes", "recorded_at"]
        read_only_fields = ["recorded_at"]
