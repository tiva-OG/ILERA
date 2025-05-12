from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers

from .models import User, FarmerProfile, VetProfile


class FarmerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FarmerProfile
        fields = "__all__"
        read_only_fields = ["user"]


class VetProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = VetProfile
        fields = "__all__"
        read_only_fields = ["user"]


class UserProfileSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    farmer_profile = FarmerProfileSerializer(read_only=True)
    vet_profile = VetProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "phone_number", "first_name", "last_name", "email", "role", "is_active", "profile"]

    def get_profile(self, obj):
        if obj.is_farmer:
            return FarmerProfileSerializer(obj.farmer_profile).data
        elif obj.is_vet:
            return VetProfileSerializer(obj.vet_profile).data
        return None


class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=[("farmer", "Farmer"), "vet", "Veterinarian"])

    class Meta:
        model = User
        fields = ["phone_number", "first_name", "last_name", "email", "role", "password"]

    def create(self, validated_data):
        role = validated_data.pop("role")
        user = User.objects.create_user(**validated_data)

        if role.lowercase() == "farmer":
            user.is_farmer = True
        elif role.lowercase() == "vet":
            user.is_vet = True
        user.save()

        return user


class CustomObtainTokenPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        phone = attrs.get("phone")
        password = attrs.get("password")
        user = User.objects.filter(phone=phone).first()

        if user and user.check_password(password):
            if not user.is_active:
                raise serializers.ValidationError("Inactive account")

            data = super().validate(attrs)
            data["user"] = {"id": user.id, "phone": user.phone}

            return data
        raise serializers.ValidationError("Invalid phone or password")

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["phone"] = user.phone

        return token
