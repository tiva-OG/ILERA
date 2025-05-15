from rest_framework.permissions import BasePermission


class IsFarmer(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, "farmer_profile")


class IsVeterinarian(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, "vet_profile")
