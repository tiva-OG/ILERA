from rest_framework import serializers


def raise_validation_error(field: str, message: str):
    raise serializers.ValidationError({field: message})
