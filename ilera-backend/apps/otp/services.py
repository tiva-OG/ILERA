from datetime import timedelta
from django.utils import timezone
import random

from .models import OTPRequest
from apps.notifications.sms_backends import SMSClient, EmailClient


class OTPService:
    EXPIRY_MINUTES = 5
    OTP_LENGTH = 5

    @classmethod
    def generate_otp(cls):
        return "".join(random.choices("0123456789", k=cls.OTP_LENGTH))

    @classmethod
    def _save_otp(cls, phone, code):
        return OTPRequest.objects.create(phone=phone, code=code)

    @classmethod
    def _send_via_email(cls, email, code):
        EmailClient.send_email(email, code)
        return f"OTP sent to email: {email}"

    @classmethod
    def _send_via_sms(cls, phone, code):
        message = f"Your ILERA verification code is {code}. It expires in {cls.EXPIRY_MINUTES} minutes. \nDon't share with anyone!"
        SMSClient.send_sms(phone, message)
        return f"OTP sent via SMS to phone: {phone}"

    @classmethod
    def send_otp(cls, phone, email=None):
        if not phone:
            raise ValueError("Phone number is required for OTP delivery.")

        code = cls.generate_otp()
        cls._save_otp(phone, code)

        try:
            if email:
                return cls._send_via_email(email, code)
            if phone:
                return cls._send_via_sms(phone, code)
        except Exception as e:
            raise RuntimeError(f"Failed to send OTP: {e}")

    @classmethod
    def verify_otp(cls, phone, code):
        try:
            otp = OTPRequest.objects.filter(phone=phone, code=code).latest("created_at")

            if otp.is_verified:
                return {"success": False, "detail": "OTP has already been used."}
            if otp.is_expired(expiry_minutes=cls.EXPIRY_MINUTES):
                return {"success": False, "detail": "OTP has expired. Please request a new one."}

            otp.is_verified = True
            otp.save()
            return {"success": True, "detail": "OTP verified successfully."}

        except OTPRequest.DoesNotExist:
            return {"success": False, "detail": "Invalid OTP. Please check the code and try again."}
