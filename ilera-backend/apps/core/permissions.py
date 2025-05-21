from rest_framework.permissions import BasePermission
from apps.vetcare.models import CareSession, SessionStatus


class IsFarmer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_farmer


class IsVet(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_vet


class IsAllowedVet(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_vet

    def has_object_permission(self, request, view, obj):
        vet = request.user.vet_profile
        farmer = obj.owner.farmer_profile

        return CareSession.objects.filter(vet=vet, farmer=farmer, status=SessionStatus.ACCEPTED).exists()


class RoleBasedPermissionMixin:
    # define permission classes for specific actions using permissions_map
    permission_map = {}

    def get_permissions(self):
        if hasattr(self, "action") and self.action in self.permission_map:
            return [perm() for perm in self.permission_map[self.action]]
        return [perm() for perm in self.permission_classes]
