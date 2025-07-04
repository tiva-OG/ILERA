from django.contrib.auth import authenticate, hashers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers

from .models import PendingUser, User, UserRole, FarmerProfile, VetProfile
from apps.core.fields import PhoneNumberField
from apps.otp.services import OTPService
from apps.core.utils.phone import normalize_nigerian_phone


# ========================================== Farmer Profile ==========================================
class FarmerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FarmerProfile
        fields = ["bio", "location", "profile_picture"]


# ========================================== Vet Profile ==========================================
class VetProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = VetProfile
        fields = ["bio", "location", "license_number", "is_available", "profile_picture"]


# ========================================== User Profile ==========================================
class UserProfileSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "phone", "first_name", "last_name", "email", "role", "is_active", "profile"]

    def get_profile(self, obj):
        if obj.is_farmer:
            return FarmerProfileSerializer(obj.farmer_profile).data
        elif obj.is_vet:
            return VetProfileSerializer(obj.vet_profile).data
        return None


# ========================================== User Signup ==========================================
class UserSignupSerializer(serializers.ModelSerializer):
    phone = PhoneNumberField()
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=[UserRole.FARMER, UserRole.VET])
    otp_message = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ["phone", "first_name", "last_name", "email", "role", "password", "otp_message"]

    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Phone number already registered with ILERA.")
        return value

    def create(self, validated_data):
        phone = validated_data["phone"]

        PendingUser.objects.filter(phone=phone).delete()

        pending_user = PendingUser.objects.create(**validated_data)

        # generate and send OTP
        message = OTPService.send_otp(pending_user.phone, email=pending_user.email)
        pending_user.otp_message = message

        return pending_user

    def get_otp_message(self, obj):
        return getattr(obj, "otp_message", None)


class UserVerifyOTPSerializer(serializers.Serializer):
    phone = PhoneNumberField()
    code = serializers.CharField()

    def validate(self, attrs):
        phone = normalize_nigerian_phone(attrs["phone"])
        code = attrs["code"]

        try:
            pending_user = PendingUser.objects.get(phone=phone)
        except PendingUser.DoesNotExist:
            raise serializers.ValidationError({"phone": "No pending signup found for this phone."})

        if pending_user.is_expired():
            raise serializers.ValidationError({"code": "OTP has expired."})

        result = OTPService.verify_otp(phone, code)

        if not result["success"]:
            raise serializers.ValidationError({"code": result["detail"]})

        user = User.objects.create_user(
            phone=pending_user.phone,
            email=pending_user.email,
            first_name=pending_user.first_name,
            last_name=pending_user.last_name,
            role=pending_user.role,
        )
        user.set_password(pending_user.password)
        user.is_active = True
        user.save()
        pending_user.delete()

        return attrs


# ========================================== Farmer Onboarding ==========================================
class FarmerOnboardingSerializer(serializers.ModelSerializer):
    class Meta:
        model = FarmerProfile
        fields = ["location", "bio"]


# ========================================== Vet Onboarding ==========================================
class VetOnboardingSerializer(serializers.ModelSerializer):
    class Meta:
        model = VetProfile
        fields = ["location", "bio", "license_number"]


# ========================================== Obtain Token ==========================================
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    phone = PhoneNumberField()
    password = serializers.CharField()

    def validate(self, attrs):
        phone = normalize_nigerian_phone(attrs["phone"])
        password = attrs["password"]

        user = authenticate(request=self.context.get("request"), phone=phone, password=password)

        if not user:
            raise serializers.ValidationError({"invalid": ["Invalid phone or password."]})

        if not user.is_active:
            OTPService.send_otp(phone)
            raise serializers.ValidationError({"invalid": ["Account not active. OTP sent for verification."]})

        refresh = self.get_token(user)
        access = refresh.access_token

        return {
            "access": str(access),
            "refresh": str(refresh),
            "user": {"id": user.id, "phone": user.phone, "fullname": user.get_fullname(), "role": user.role},
        }


# ========================================== Read Vet ==========================================
class VetListSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="user.id", read_only=True)
    fullname = serializers.CharField(source="user.get_fullname", read_only=True)
    phone = PhoneNumberField(source="user.phone", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    session = serializers.SerializerMethodField()

    class Meta:
        model = VetProfile
        fields = ["id", "fullname", "phone", "email", "location", "bio", "license_number", "is_available", "profile_picture", "session"]

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


class FarmerListSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="user.id", read_only=True)
    fullname = serializers.CharField(source="user.get_fullname", read_only=True)
    phone = PhoneNumberField(source="user.phone", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    session = serializers.SerializerMethodField()

    class Meta:
        model = FarmerProfile
        fields = ["id", "fullname", "phone", "email", "location", "bio", "profile_picture", "session"]

    def get_session(self, vet):
        sessions = getattr(vet, "sessions_with_vet", [])

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
