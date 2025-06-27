from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import CareSession, HealthRecord, SessionStatus
from .serializers import CareSessionSerializer, HealthRecordSerializer
from apps.core.permissions import IsFarmer, IsVet, RoleBasedPermissionMixin


# let it be that if action in ['decline', 'cancel'] then instance be deleted


class CareSessionViewSet(RoleBasedPermissionMixin, viewsets.ModelViewSet):
    serializer_class = CareSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    permission_map = {
        "accept": [IsVet],
        "decline": [IsVet],
        "cancel": [IsFarmer],
        "create": [IsFarmer],
        "conclude": [IsVet | IsFarmer],
    }

    def get_queryset(self):
        user = self.request.user
        if user.is_vet:
            return CareSession.objects.filter(vet=user.vet_profile)
        elif user.is_farmer:
            return CareSession.objects.filter(farmer=user.farmer_profile)

        return CareSession.objects.none()

    def perform_create(self, serializer):
        print("CREATING A VETCARE REQUEST")
        serializer.save()

    @action(detail=True, methods=["POST"])
    def accept(self, request, pk=None):
        session = self.get_object()

        # add control that session has to be PENDING
        if session.status != SessionStatus.PENDING:
            return Response({"error": "Bad Request"}, status=400)

        if session.vet.user != request.user:
            return Response({"error": "Unauthorized"}, status=403)

        session.start()
        return Response({"status": "accepted"})

    @action(detail=True, methods=["POST"])
    def conclude(self, request, pk=None):
        session = self.get_object()

        # add control that session has to be ACCEPTED
        if session.status != SessionStatus.ACCEPTED:
            return Response({"error": "Bad Request"}, status=400)

        if (session.farmer.user != request.user) and (session.vet.user != request.user):
            return Response({"error": "Unauthorized"}, status=403)

        session.conclude()
        return Response({"status": "concluded"})

    @action(detail=True, methods=["POST"])
    def cancel(self, request, pk=None):
        session = self.get_object()

        # add control that session has to be pending
        if session.status != SessionStatus.PENDING:
            return Response({"error": "Bad Request"}, status=400)

        if session.farmer.user != request.user:
            return Response({"error": "Unauthorized"}, status=403)

        session.cancel()
        return Response({"status": "cancelled"})

    @action(detail=True, methods=["POST"])
    def decline(self, request, pk=None):
        session = self.get_object()

        # add control that session has to be pending
        if session.status != SessionStatus.PENDING:
            return Response({"error": "Bad Request"}, status=400)

        if session.vet.user != request.user:
            return Response({"error": "Unauthorized"}, status=403)

        session.decline()
        return Response({"status": "declined"})

    # TODO: remove action
    @action(detail=True, methods=["POST"])
    def remove(self, request, pk=None):
        session = self.get_object()

        session.delete()
        return Response({"status": "deleted"})


class HealthRecordViewSet(viewsets.ModelViewSet):
    queryset = HealthRecord.objects.all()
    serializer_class = HealthRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_vet:
            return HealthRecord.objects.filter(session__vet=user.vet_profile)
        elif user.is_farmer:
            return HealthRecord.objects.filter(session__farmer=user.farmer_profile)

        return HealthRecord.objects.none()
