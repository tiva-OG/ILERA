from rest_framework.permissions import BasePermission
from apps.vetcare.models import CareSession, SessionStatus


class IsFarmer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_farmer


class IsVet(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_vet


class IsFarmerOrVetInSession(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.is_farmer or request.user.is_vet)

    def has_object_permission(self, request, view, obj):
        if request.user.is_farmer:
            return obj.owner == request.user
        elif request.user.is_vet:
            return CareSession.objects.filter(
                vet=request.user.vet_profile,
                farmer=obj.owner.farmer_profile,
                status=SessionStatus.ACCEPTED,
            ).exists()

        return False


class RoleBasedPermissionMixin:
    # define permission classes for specific actions using permissions_map
    permission_map = {}

    def get_permissions(self):
        if hasattr(self, "action") and self.action in self.permission_map:
            return [perm() for perm in self.permission_map[self.action]]
        return [perm() for perm in self.permission_classes]
