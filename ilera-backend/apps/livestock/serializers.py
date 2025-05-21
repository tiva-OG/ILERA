from datetime import date
from rest_framework import serializers

from .models import Livestock
from apps.sensors.models import SensorDevice
from apps.vetcare.models import HealthRecord


class HealthRecordSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthRecord
        fields = ["id", "record_type", "notes", "recorded_at"]


class LivestockListSerializer(serializers.ModelSerializer):
    sensor_id = serializers.SerializerMethodField()

    class Meta:
        model = Livestock
        fields = ["id", "tag_id", "category", "breed", "health_status", "sensor_id"]

    def get_sensor_id(self, obj):
        return obj.sensor_device.device_id if hasattr(obj, "sensor_device") else None


class LivestockDetailSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField()
    sensor_id = serializers.SerializerMethodField()
    records = HealthRecordSummarySerializer(many=True, read_only=True)

    class Meta:
        model = Livestock
        fields = ["id", "tag_id", "category", "breed", "gender", "age", "registered_at", "health_status", "sensor_id", "records"]
        read_only_fields = ["id", "registered_at"]

    def get_age(self, obj):
        return date.today().year - obj.birth_year

    def get_sensor_id(self, obj):
        return obj.sensor_device.device_id if hasattr(obj, "sensor_device") else None


class LivestockWriteSerializer(serializers.ModelSerializer):
    age = serializers.IntegerField(write_only=True, required=True)
    sensor_id = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Livestock
        fields = ["id", "tag_id", "category", "breed", "gender", "age", "sensor_id"]
        read_only_fields = ["id"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["age"] = date.today().year - instance.birth_year
        rep.pop("birth_year", None)

        return rep

    def validate_sensor_id(self, sensor_id):
        try:
            sensor = SensorDevice.objects.get(device_id=sensor_id)
            if hasattr(sensor, "livestock") and sensor.livestock_id:
                raise serializers.ValidationError(f"Sensor '{sensor_id}' is already assigned to '{sensor.livestock.get_fullname()}'.")
        except SensorDevice.DoesNotExist:
            pass  # to be created in create()

        return sensor_id

    def create(self, validated_data):
        owner = self.context["request"].user
        age = validated_data.pop("age")
        sensor_id = validated_data.pop("tracker_id", None)
        validated_data["birth_year"] = date.today().year - age

        livestock = Livestock.objects.create(owner=owner, **validated_data)

        if sensor_id:
            SensorDevice.objects.update_or_create(device_id=sensor_id, livestock=livestock)

        return livestock

    def update(self, instance, validated_data):
        if "age" in validated_data:
            age = validated_data.pop("age")
            validated_data["birth_year"] = date.today().year - age

        sensor_id = validated_data.pop("tracker_id", None)
        livestock = super().update(instance, validated_data)

        if sensor_id:
            try:
                existing_sensor = SensorDevice.objects.get(device_id=sensor_id)
                if existing_sensor.livestock != instance:
                    raise serializers.ValidationError(f"Sensor '{sensor_id}' is already assigned to '{existing_sensor.livestock.get_fullname()}'.")
            except SensorDevice.DoesNotExist:
                SensorDevice.objects.create(device_id=sensor_id, livestock=instance)

        return livestock
