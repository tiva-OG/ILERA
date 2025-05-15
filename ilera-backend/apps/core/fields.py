import re
from rest_framework import serializers

from .utils.phone import normalize_nigerian_phone

NIGERIAN_PHONE_REGEX = r"^(\+234|0)[789][01]\d{8}$"


class PhoneNumberField(serializers.CharField):
    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        normalized = normalize_nigerian_phone(data)
        if not re.match(NIGERIAN_PHONE_REGEX, normalized):
            raise serializers.ValidationError("Enter a valid Nigerian phone number (e.g., 08012345678 or +2348012345678).")
        return normalized
