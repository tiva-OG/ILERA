from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, views, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from .models import Livestock
from .serializers import LivestockSerializer
from apps.core.permissions import IsFarmer, IsVet, RoleBasedPermissionMixin
from apps.vetcare.models import CareSession, SessionStatus


class LivestockListCreateView(generics.ListCreateAPIView):
    serializer_class = LivestockSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmer]

    def get_queryset(self):
        user = self.request.user
        if user.is_farmer:
            return Livestock.objects.filter(owner=user)
        elif user.is_vet:
            # return the livestock of farmer the user (vet) is having a session with
            return Livestock.objects.filter(
                owner__farmer_profile__sessions__vet=user.vet_profile,
                owner__farmer_profile__sessions__status=SessionStatus.ACCEPTED,
            ).distinct()

        return Livestock.objects.none()

    def perform_create(self, serializer):
        user = self.request.user

        if user.is_farmer:
            serializer.save(owner=user)
            return Response({"status": "created", "data": serializer.data})

        return Response({"error": "Unauthorized"}, status=403)


class LivestockDeleteView(generics.DestroyAPIView):
    queryset = Livestock.objects.all()
    serializer_class = LivestockSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmer]

    def perform_destroy(self, instance):
        user = self.request.user

        if user != instance.owner:
            return Response({"error": "Unauthorized"}, status=403)

        instance.delete()
        return Response({"status": "deleted"}, status=205)


class LivestockArchiveView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, IsFarmer]

    def patch(self, request, pk=None, *args, **kwargs):
        user = request.user

        try:
            livestock = Livestock.objects.get(pk=pk)

            if user != livestock.owner:
                return Response({"error": "Unauthorized"}, status=403)

            livestock.is_archived = True
            livestock.save()

            return Response({"status": "archived"}, status=200)
        except Livestock.DoesNotExist:
            return Response({"detail": "Livestock not found."}, status=404)


class LivestockViewSet(viewsets.ModelViewSet):
    serializer_class = LivestockSerializer
    permission_classes = [permissions.IsAuthenticated]
    permission_map = {
        "create": [IsFarmer],
        "archive": [IsFarmer],
        "unarchive": [IsFarmer],
    }
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["gender", "category", "is_archived"]
    search_fields = ["tag_id", "breed", "category"]

    def get_queryset(self):
        user = self.request.user
        queryset = Livestock.objects.all()

        if user.is_farmer:
            return queryset.filter(owner=user)
        elif user.is_vet:
            active_sessions = CareSession.objects.filter(vet=user.vet_profile, status=SessionStatus.ACCEPTED)
            farmer_ids = active_sessions.values_list("farmer__user__id", flat=True)
            return queryset.filter(owner__id__in=farmer_ids)

        return Livestock.objects.none()

    @action(detail=True, methods=["POST"])
    def archive(self, request, pk=None):
        livestock = self.get_object()
        livestock.is_archived = True
        livestock.save()

        return Response({"status": "archived"}, status=200)

    @action(detail=True, methods=["POST"])
    def unarchive(self, request, pk=None):
        livestock = self.get_object()
        livestock.is_archived = False
        livestock.save()

        return Response({"status": "unarchived"}, status=200)
