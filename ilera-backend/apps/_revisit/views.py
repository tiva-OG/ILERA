from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend

from .models import Appointment
from .filters import AppointmentFilter
from .serializer import AppointmentSerializer
from apps.core.permissions import IsFarmer, IsVeterinarian


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmer, IsVeterinarian]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = AppointmentFilter
    search_fields = ["livestock__category"]  # enables to search by category
    ordering_fields = ["scheduled_time", "created_at"]

    def get_queryset(self):
        user = self.request.user

        if user.is_farmer:
            return self.queryset.filter(farmer=user.farmer_profile)
        elif user.is_vet:
            return self.queryset.filter(vet=user.vet_profile)

        return Appointment.objects.none()

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user

        if user.is_vet:
            if instance.status in ["CANCELLED", "COMPLETED"]:  # user can do nothing after appointment is cancelled or completed
                raise PermissionDenied("Cannot modify a cancelled or completed appointment.")

            data = request.data
            status = data.get("status")
            scheduled_time = data.get("scheduled_time")
            notes = data.get("notes")

            if status:
                if status not in ["ACCEPTED", "DECLINED", "COMPLETED"]:
                    raise ValidationError("Invalid status value.")
                instance.status = status

            if scheduled_time:
                instance.scheduled_time = scheduled_time
            if notes:
                instance.notes = notes
            instance.save()

            serializer = self.get_serializer(instance)
            return Response(serializer.data, status=200)
        else:
            raise PermissionError("Only the assigned vet can update the appointment.")

    @action(detail=True, methods=["PATCH"], url_path="cancel")
    def cancel(self, request, pk=None):
        appointment = self.get_object()
        user = request.user

        if user.is_farmer and appointment.status == "PENDING":  # only allow farmer to cancel appointment if pending
            if appointment.farmer != user.farmer_profile:
                return Response({"detail": "Unauthorized user."}, status=403)

            appointment.status = "CANCELLED"
            appointment.save()
            return Response({"detail": "Appointment has been cancelled."})

        return Response({"detail": "Only pending appointments can be cancelled by the farmer."}, status=400)

    @action(detail=True, methods=["PATCH"], url_path="complete")
    def complete(self, request, pk=None):
        appointment = self.get_object()
        user = request.user

        if user.is_vet and appointment.vet == user.vet_profile:  # only allow appointed vet to mark appointment as complete
            if appointment.status != "ACCEPTED":
                return Response({"detail": "Only accepted appointments can be marked complete."}, status=400)

            appointment.status = "COMPLETED"
            appointment.save()
            return Response({"detail": "Appointment marked as complete."})

        return Response({"detail": "Unauthorized user."}, status=403)
