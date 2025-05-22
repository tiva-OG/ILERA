import re
import ulid
from django.db import models
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


class ULIDField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = 26
        kwargs["unique"] = True
        kwargs.setdefault("editable", False)
        kwargs.setdefault("primary_key", True)
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname)
        if add and not value:
            ulid_str = ulid.new().str
            setattr(model_instance, self.attname, ulid_str)
            return ulid_str
        return value
