from rest_framework import serializers

from .models import CareSession, HealthRecord, SessionStatus
from apps.core.fields import PhoneNumberField
from apps.users.models import FarmerProfile, VetProfile


class CareSessionSerializer(serializers.ModelSerializer):
    farmer_name = serializers.CharField(source="farmer.user.get_fullname", read_only=True)
    vet_name = serializers.CharField(source="vet.user.get_fullname", read_only=True)
    status = serializers.ChoiceField(choices=SessionStatus.choices, allow_null=True, required=False)
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = CareSession
        fields = ["id", "vet", "status", "created_at", "started_at", "ended_at", "is_active", "farmer_name", "vet_name"]
        read_only_fields = ["status", "created_at", "started_at", "ended_at", "is_active", "farmer_name", "vet_name"]

    def create(self, validated_data):
        request = self.context["request"]
        farmer_profile = request.user.farmer_profile
        vet_profile = validated_data["vet"]

        active_session = CareSession.objects.filter(farmer=farmer_profile, vet=vet_profile, status__in=[SessionStatus.ACCEPTED, SessionStatus.PENDING]).exists()

        if active_session:
            raise serializers.ValidationError("A pending or ongoing session already exists with this vet.")

        

        # existing_session = CareSession.objects.filter(farmer=farmer_profile, vet=vet_profile, status__in=[SessionStatus.DECLINED, None]).first()

        # if existing_session:
        #     existing_session.status = SessionStatus.PENDING
        #     existing_session.started_at = None
        #     existing_session.ended_at = None
        #     existing_session.has_history = False
        #     existing_session.save()

        #     return existing_session

        # if CareSession.objects.filter(farmer=farmer_profile, vet=vet_profile, status__in=[SessionStatus.PENDING, SessionStatus.ACCEPTED]).exists():
        #     raise serializers.ValidationError("A pending or an ongoing session already exists with this vet.")

        return CareSession.objects.create(farmer=farmer_profile, vet=vet_profile, status=SessionStatus.PENDING)


class VetcareVetProfileSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(source="user.get_fullname", read_only=True)
    session = serializers.SerializerMethodField()

    class Meta:
        model = VetProfile
        fields = ["id", "fullname", "location", "bio", "license_number", "is_available", "session"]

    def get_session(self, vet):
        request = self.context.get("request")
        if not request or not hasattr(request.user, "farmer_profile"):
            return None
        farmer = request.user.farmer_profile

        latest_session = CareSession.objects.filter(farmer=farmer, vet=vet).order_by("-created_at").first()
        # latest_session CareSession.objects.filter(farmer=farmer, vet=vet, status__in=[SessionStatus.ACCEPTED, SessionStatus.PENDING])..order_by("-created_at").first()

        if latest_session:
            return {
                "id": latest_session.id,
                "status": latest_session.status,
                "created_at": latest_session.created_at,
                "started_at": latest_session.started_at,
                "ended_at": latest_session.ended_at,
                "has_history": latest_session.status == SessionStatus.CONCLUDED,
            }
        return None


class FarmerListSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="user.id", read_only=True)
    fullname = serializers.CharField(source="user.get_fullname", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    session = serializers.SerializerMethodField()

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
            "fullname": vet_user.get_fullname(),
            "phone": vet_user.phone,
            "email": vet_user.email,
            "location": obj.vet.location,
            "bio": obj.vet.bio,
            "is_available": obj.vet.is_available,
        }


class FarmerListSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="user.id", read_only=True)
    fullname = serializers.CharField(source="user.get_fullname", read_only=True)
    phone = PhoneNumberField(source="user.phone", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    session = serializers.SerializerMethodField()

    class Meta:
        model = FarmerProfile
        fields = ["id", "fullname", "phone", "email", "location", "bio", "session"]

    def get_session(self, vet):
        sessions = getattr(vet, "sessions_with_farmer", [])

        if sessions:
            session = sessions[0]
            return {
                "id": session.id,
                "status": session.status,
                "created_at": session.created_at,
                "started_at": session.started_at,
                "ended_at": session.ended_at,
                "has_history": session.has_history,
            }

        return None


class HealthRecordSerializer(serializers.ModelSerializer):
    livestock_name = serializers.CharField(source="livestock.get_fullname", read_only=True)

    class Meta:
        model = HealthRecord
        fields = ["id", "session", "livestock", "livestock_name", "record_type", "notes", "recorded_at"]
        read_only_fields = ["recorded_at"]
