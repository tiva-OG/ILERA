from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Appointment

User = get_user_model()


class AppointmentSerializer(serializers.ModelSerializer):
    farmer = serializers.StringRelatedField(read_only=True)
    vet = serializers.StringRelatedField(read_only=True)
    livestock = serializers.PrimaryKeyRelatedField(queryset=None)  # set dynamically

    class Meta:
        model = Appointment
        fields = ["id", "farmer", "vet", "livestock", "status", "request_time", "scheduled_time", "notes"]
        read_only_fields = ["id", "status", "request_time", "farmer", "vet"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")

        if request and request.user.is_farmer:
            self.fields["livestock"].queryset = request.user.farmer_profile.livestock.all()  # restricts farmer to their own animals

    def create(self, validated_data):
        request = self.context.get("request")
        farmer = request.user.farmer_profile
        vet_id = request.data.get("vet_id")
        vet = User.objects.get(id=vet_id).vet_profile

        appointment = Appointment.objects.create(farmer=farmer, vet=vet, status="PENDING", **validated_data)

        return appointment
