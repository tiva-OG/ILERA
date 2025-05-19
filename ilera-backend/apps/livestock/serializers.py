from datetime import date
from rest_framework import serializers

from .models import Livestock
from apps.vetcare.models import HealthRecord


class HealthRecordSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthRecord
        fields = ["id", "record_type", "notes", "recorded_at"]


class LivestockSerializer(serializers.ModelSerializer):
    age = serializers.IntegerField(write_only=True, required=True)
    # age = serializers.SerializerMethodField(read_only=True)
    records = HealthRecordSummarySerializer(many=True, read_only=True)

    class Meta:
        model = Livestock
        fields = ["id", "tag_id", "category", "breed", "gender", "age", "image", "registered_at", "is_archived", "records"]
        read_only_fields = ["id", "registered_at", "image"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["age"] = date.today().year - instance.birth_year
        rep.pop("birth_year", None)

        return rep

    def create(self, validated_data):
        age = validated_data.pop("age")
        validated_data["birth_year"] = date.today().year - age
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "age" in validated_data:
            age = validated_data.pop("age")
            validated_data["birth_year"] = date.today().year - age
        return super().update(instance, validated_data)
