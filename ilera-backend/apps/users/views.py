from django.conf import settings
from django.db import transaction
from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, generics, permissions, status, views
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


from .models import User, FarmerProfile, VetProfile
from .serializers import (
    UserSignupSerializer,
    UserVerifyOTPSerializer,
    UserProfileSerializer,
    CustomTokenObtainPairSerializer,
    FarmerOnboardingSerializer,
    VetOnboardingSerializer,
    FarmerProfileSerializer,
    VetProfileSerializer,
    VetListSerializer,
    FarmerListSerializer,
)
from apps.vetcare.models import CareSession, SessionStatus
from apps.core.permissions import IsFarmer, IsVet
from apps.core.utils.phone import normalize_nigerian_phone


# ========================================== Create new user ==========================================
class UserSignupView(generics.CreateAPIView):
    serializer_class = UserSignupSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        print("CREATING USER!")
        print("REQUEST DATA:", request.data)
        response = super().create(request, *args, **kwargs)
        return Response({"user": response.data}, status=201)


# ========================================== Verify user signup OTP ==========================================
class UserVerifyOTPView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserVerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response({"detail": "OTP verified successfully."}, status=status.HTTP_200_OK)


# ========================================== Onboard user ==========================================
class UserOnboardingView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def patch(self, request, *args, **kwargs):
        phone = request.data.get("phone")
        profile_data = request.data.get("profile")
        user = User.objects.get(phone=normalize_nigerian_phone(phone))

        if user.is_farmer:
            farmer_profile = user.farmer_profile
            serializer = FarmerOnboardingSerializer(farmer_profile, data=profile_data, partial=True)
        elif user.is_vet:
            vet_profile = user.vet_profile
            serializer = VetOnboardingSerializer(vet_profile, data=profile_data, partial=True)
        else:
            return Response({"detail": "User profile not found."}, status=404)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=200)


# ========================================== View and update user profile ==========================================
class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self):
        return self.request.user

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        user = self.get_object()

        user_serializer = self.get_serializer(user, data=request.data, partial=True)
        user_serializer.is_valid(raise_exception=True)
        user_serializer.save()

        # update the nested profile provided
        profile_data = {}
        profile_keys = ["bio", "location", "profile_picture", "license_number", "is_available"]

        for key in request.data:
            if key in profile_keys:
                profile_data[key] = request.data[key]

        if profile_data:
            if user.is_farmer:
                profile = user.farmer_profile
                serializer_class = FarmerProfileSerializer
            elif user.is_vet:
                profile = user.vet_profile
                serializer_class = VetProfileSerializer
            else:
                return Response({"detail": "Unknown user role."}, status=400)

            new_image = profile_data.get("profile_picture")
            if new_image and profile.profile_picture and profile.profile_picture != new_image:
                profile.profile_picture.delete(save=False)

            profile_serializer = serializer_class(profile, data=profile_data, partial=True)
            profile_serializer.is_valid(raise_exception=True)
            profile_serializer.save()

        return Response(self.get_serializer(user).data, status=200)


# ========================================== Obtain token on login ==========================================
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        refresh_token = response.data.get("refresh", None)

        if refresh_token:
            response.set_cookie(
                key=settings.SIMPLE_JWT["AUTH_COOKIE"],
                value=str(refresh_token),
                httponly=True,
                secure=settings.SIMPLE_JWT.get("AUTH_COOKIE_SECURE", False),
                samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
                max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
            )

        return response


# ========================================== Refresh token ==========================================
class CustomTokenRefreshView(TokenRefreshView):

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh") or request.COOKIES.get(settings.SIMPLE_JWT.get("AUTH_COOKIE", "refresh_token"))

        if refresh_token is None:
            return Response({"detail": "No refresh token provided"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            token = RefreshToken(refresh_token)
            access_token = str(token.access_token)

            response = Response({"access": access_token}, status=status.HTTP_200_OK)

            return response

        except Exception as e:
            return Response({"detail": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)


# ========================================== Logout user ==========================================
class LogoutView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh") or request.COOKIES.get("refresh_token")

        if refresh_token is None:
            return Response({"detail": "No refresh token provided."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            # also blacklist access token

            response = Response({"detail": "Logout successful."}, status=status.HTTP_205_RESET_CONTENT)
            response.delete_cookie("refresh_token")

            return response

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ========================================== List Vets (for Farmers) ==========================================
class VetListView(generics.ListAPIView):
    permission_classes = [IsFarmer]
    serializer_class = VetListSerializer

    def get_queryset(self):
        farmer = self.request.user.farmer_profile

        queryset = VetProfile.objects.select_related("user").prefetch_related(
            Prefetch("sessions", queryset=CareSession.objects.filter(farmer=farmer).order_by("-created_at"), to_attr="sessions_with_farmer")
        )

        return queryset

    def get_serializer_context(self):
        return {"request": self.request}


class VetDetailView(generics.RetrieveAPIView):
    permission_classes = [IsFarmer]
    serializer_class = VetListSerializer
    lookup_url_kwarg = "vet_id"

    def get_queryset(self):
        farmer = self.request.user.farmer_profile
        queryset = VetProfile.objects.select_related("user").prefetch_related(
            Prefetch("sessions", queryset=CareSession.objects.filter(farmer=farmer), to_attr="sessions_with_farmer")
        )

        return queryset

    def get_object(self):
        queryset = self.get_queryset()
        vet_id = self.kwargs.get(self.lookup_url_kwarg)
        return get_object_or_404(queryset, user__id=vet_id)


class FarmerListView(generics.ListAPIView):
    permission_classes = [IsVet]
    serializer_class = FarmerListSerializer

    def get_queryset(self):
        vet = self.request.user.vet_profile
        sessions = (
            CareSession.objects.filter(vet=vet)
            .filter(Q(status__in=[SessionStatus.ACCEPTED, SessionStatus.PENDING]) | Q(has_history=True))
            .order_by("-created_at")
        )

        queryset = (
            FarmerProfile.objects.select_related("user")
            .prefetch_related(Prefetch("sessions", queryset=sessions, to_attr="sessions_with_vet"))
            .filter(sessions__in=sessions)
            .distinct()
        )

        return queryset

    def get_serializer_context(self):
        return {"request": self.request}


class FarmerDetailView(generics.RetrieveAPIView):
    permission_classes = [IsVet]
    serializer_class = FarmerListSerializer
    lookup_url_kwarg = "farmer_id"

    def get_queryset(self):
        vet = self.request.user.vet_profile
        sessions = (
            CareSession.objects.filter(vet=vet)
            .filter(Q(status__in=[SessionStatus.ACCEPTED, SessionStatus.PENDING]) | Q(has_history=True))
            .order_by("-created_at")
        )

        queryset = (
            FarmerProfile.objects.select_related("user")
            .prefetch_related(Prefetch("sessions", queryset=sessions, to_attr="sessions_with_vet"))
            .filter(sessions__in=sessions)
            .distinct()
        )

        return queryset

    def get_object(self):
        queryset = self.get_queryset()
        farmer_id = self.kwargs.get(self.lookup_url_kwarg)
        return get_object_or_404(queryset, user__id=farmer_id)
