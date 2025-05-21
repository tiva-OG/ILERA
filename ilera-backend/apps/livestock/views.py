from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from .models import Livestock
from .serializers import LivestockListSerializer, LivestockDetailSerializer, LivestockWriteSerializer
from apps.core.permissions import IsFarmer, IsAllowedVet, RoleBasedPermissionMixin
from apps.vetcare.models import CareSession, SessionStatus


class LivestockViewSet(RoleBasedPermissionMixin, viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    permission_map = {"create": [IsFarmer], "retrieve": [IsFarmer | IsAllowedVet]}
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["gender", "category"]
    search_fields = ["tag_id", "breed", "category"]

    def get_serializer_class(self):
        if self.action == "list":
            return LivestockListSerializer
        elif self.action == "retrieve":
            return LivestockDetailSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return LivestockWriteSerializer

        return LivestockDetailSerializer

    def get_queryset(self):
        user = self.request.user
        farmer_id = self.request.query_params.get("farmer_id")
        queryset = Livestock.objects.all()

        if self.action == "retrieve" and user.is_vet:
            return queryset

        if user.is_farmer:
            return queryset.filter(owner=user)
        elif user.is_vet and farmer_id:
            vet = user.vet_profile
            has_access = CareSession.objects.filter(vet=vet, farmer__user__id=farmer_id, status=SessionStatus.ACCEPTED).exists()

            if has_access:
                return queryset.filter(owner__id=farmer_id)

        return Livestock.objects.none()

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=False, methods=["GET"], url_path="category-summary")
    def category_summary(self, request):
        queryset = self.get_queryset()

        data = queryset.values("category").annotate(count=Count("id")).order_by("category")
        result = {item["category"]: item["count"] for item in data}

        return Response(result, status=200)
