from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import CareSession, HealthRecord
from .serializers import CareSessionSerializer, HealthRecordSerializer
from apps.users.models import FarmerProfile, VetProfile
from apps.core.permissions import IsFarmer, IsVet


class CareSessionViewSet(viewsets.ModelViewSet):
    queryset = CareSession.objects.all()
    serializer_class = CareSessionSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmer, IsVet]

    def get_queryset(self):
        user = self.request.user
        if user.is_vet:
            return CareSession.objects.filter(vet=user.vet_profile)
        elif user.is_farmer:
            return CareSession.objects.filter(farmer=user.farmer_profile)

        return CareSession.objects.none()

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["POST"])
    def accept(self, request, pk=None):
        session = self.get_object()

        if session.vet.user != request.user:
            return Response({"error": "Unauthorized"}, status=403)

        session.start()
        return Response({"status": "accepted."})

    @action(detail=True, methods=["POST"])
    def complete(self, request, pk=None):
        session = self.get_object()

        if session.vet.user != request.user:
            return Response({"error": "Unauthorized"}, status=403)

        session.complete()
        return Response({"status": "completed"})


class HealthRecordViewSet(viewsets.ModelViewSet):
    queryset = HealthRecord.objects.all()
    serializer_class = HealthRecordSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmer, IsVet]

    def get_queryset(self):
        user = self.request.user
        if user.is_vet:
            return HealthRecord.objects.filter(session__vet=user.vet_profile)
        elif user.is_farmer:
            return HealthRecord.objects.filter(session__farmer=user.farmer_profile)

        return HealthRecord.objects.none()
