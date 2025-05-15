from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
import re

from .models import User, FarmerProfile, VetProfile
from apps.core.fields import PhoneNumberField
from apps.otp.services import OTPService
from apps.core.utils.phone import normalize_nigerian_phone


# ========================================== Farmer Profile ==========================================
class FarmerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FarmerProfile
        fields = "__all__"
        read_only_fields = ["user"]


# ========================================== Vet Profile ==========================================
class VetProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = VetProfile
        fields = "__all__"
        read_only_fields = ["user"]


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
    role = serializers.ChoiceField(choices=["farmer", "vet"])
    otp_message = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ["phone", "first_name", "last_name", "email", "role", "password", "otp_message"]

    def create(self, validated_data):
        password = validated_data.pop("password")

        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()

        # generate and send otp
        message = OTPService.send_otp(user.phone, email=user.email)
        user.otp_message = message

        return user

    def get_otp_message(self, obj):
        return getattr(obj, "otp_message", None)


# ========================================== Obtain Token ==========================================
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    phone = PhoneNumberField()
    password = serializers.CharField()

    def validate(self, attrs):
        phone = normalize_nigerian_phone(attrs.get("phone"))
        password = attrs.get("password")

        user = authenticate(request=self.context.get("request"), phone=phone, password=password)

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        if not user.is_active:
            OTPService.send_otp(phone)
            raise serializers.ValidationError("OTP sent. Please verify to activate your account.")

        refresh = self.get_token(user)
        access = refresh.access_token

        return {
            "access": str(access),
            "refresh": str(refresh),
            "user": {"id": user.id, "phone": user.phone},
        }
