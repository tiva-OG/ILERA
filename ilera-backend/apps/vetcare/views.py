from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import CareSession, HealthRecord, SessionStatus
from .serializers import CareSessionSerializer, HealthRecordSerializer, VetSessionSerializer, FarmerSessionSerializer
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
        "terminate": [IsVet | IsFarmer],
    }

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

        # add control that session has to be pending
        if session.status != SessionStatus.PENDING:
            return Response({"error": "Bad Request"}, status=400)

        if session.vet.user != request.user:
            return Response({"error": "Unauthorized"}, status=403)

        session.start()
        return Response({"status": "accepted"})

    @action(detail=True, methods=["POST"])
    def terminate(self, request, pk=None):
        session = self.get_object()

        # add control that session has to accepted
        if session.status != SessionStatus.ACCEPTED:
            return Response({"error": "Bad Request"}, status=400)

        if (session.farmer.user != request.user) and (session.vet.user != request.user):
            return Response({"error": "Unauthorized"}, status=403)

        session.terminate()
        return Response({"status": "terminated"})

    @action(detail=True, methods=["POST"])
    def cancel(self, request, pk=None):
        session = self.get_object()

        # add control that session has to be pending
        if session.status != SessionStatus.PENDING:
            return Response({"error": "Bad Request"}, status=400)

        if session.farmer.user != request.user:
            return Response({"error": "Unauthorized"}, status=403)

        session.cancel()
        # session.delete()
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
        # session.delete()
        return Response({"status": "declined"})

    @action(detail=False, methods=["GET"], url_path="vet-session", serializer_class=VetSessionSerializer)
    def vet_session(self, request):
        vet = request.user.vet_profile
        # terminated_param = request.query_params.get("terminated", "").lower()

        # session_status = [SessionStatus.TERMINATED] if terminated_param == "true" else [SessionStatus.ACCEPTED, SessionStatus.PENDING]

        # sessions = CareSession.objects.filter(vet=vet, status__in=session_status).order_by("created_at")
        sessions = self._get_sessions(vet=vet)
        serializer = self.get_serializer(sessions, many=True)

        return Response(serializer.data)

    @action(detail=False, methods=["GET"], url_path="farmer-session", serializer_class=FarmerSessionSerializer)
    def farmer_session(self, request):
        farmer = request.user.farmer_profile
        sessions = self._get_sessions(farmer=farmer)
        # terminated_param = request.query_params.get("terminated", "").lower()

        # session_status = [SessionStatus.TERMINATED] if terminated_param == "true" else [SessionStatus.ACCEPTED, SessionStatus.PENDING]

        # sessions = CareSession.objects.filter(farmer=farmer, status__in=session_status).order_by("created_at")
        serializer = self.get_serializer(sessions, many=True)

        return Response(serializer.data)

    ####### helper function #######
    def _get_sessions(self, **filters):
        terminated_param = self.request.query_params.get("terminated", "").lower()
        statuses = [SessionStatus.TERMINATED] if terminated_param == "true" else [SessionStatus.ACCEPTED, SessionStatus.PENDING]

        return CareSession.objects.filter(status__in=statuses, **filters).order_by("created_at")


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
