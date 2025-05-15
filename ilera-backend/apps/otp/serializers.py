from django.contrib.auth import get_user_model
from rest_framework import serializers
import re

from .services import OTPService
from apps.core.fields import PhoneNumberField
from apps.core.utils.phone import normalize_nigerian_phone

User = get_user_model()


class OTPSendSerializer(serializers.Serializer):
    phone = PhoneNumberField(required=False)
    email = serializers.EmailField(required=False)
    otp_message = serializers.SerializerMethodField(read_only=True)

    def validate(self, attrs):
        phone = attrs.get("phone")
        email = attrs.get("email")

        if not phone and not email:
            raise serializers.ValidationError("At least one of phone or email is required.")

        if not phone:
            user = User.objects.get(email=email)
            phone = user.phone
            
        phone = normalize_nigerian_phone(phone)
        message = OTPService.send_otp(phone, email)
        self.otp_message = message

        return attrs

    def get_otp_message(self, obj):
        return getattr(self, "otp_message", None)

class OTPVerifySerializer(serializers.Serializer):
    phone = PhoneNumberField()
    code = serializers.CharField()

    def validate(self, attrs):
        phone = normalize_nigerian_phone(attrs.get("phone"))
        code = attrs.get("code")

        result = OTPService.verify_otp(phone, code)

        if result["success"]:
            try:
                user = User.objects.get(phone=phone)
                user.is_active = True
                user.save()

                return attrs

            except User.DoesNotExist:
                raise serializers.ValidationError("User with this phone number does not exist.")
        else:
            raise serializers.ValidationError(result["detail"])
