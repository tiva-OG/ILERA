from django.conf import settings
from django.db import transaction
from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import User
from .serializers import UserSignupSerializer, UserProfileSerializer, CustomTokenObtainPairSerializer, FarmerProfileSerializer, VetProfileSerializer


# ========================================== Create new user ==========================================
class UserSignupView(generics.CreateAPIView):
    serializer_class = UserSignupSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({"user": response.data}, status=status.HTTP_201_CREATED)


# ========================================== View and update user profile ==========================================
class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        user = self.get_object()
        user_serializer = self.get_serializer(user, data=request.data, partial=True)
        user_serializer.is_valid(raise_exception=True)
        user_serializer.save()

        # update the nested profile provided
        profile_data = request.data.get("profile")
        if profile_data:
            if user.is_farmer:
                profile = user.farmer_profile
                profile_serializer = FarmerProfileSerializer(profile, data=profile_data, partial=True)
            elif user.is_vet:
                profile = user.vet_profile
                profile_serializer = VetProfileSerializer(profile, data=profile_data, partial=True)
            else:
                return Response({"detail": "Unknown user role."}, status=400)

            profile_serializer.is_valid(raise_exception=True)
            profile_serializer.save()

        return Response(self.get_serializer(user).data, status=200)


# ========================================== Obtain token on login ==========================================
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        refresh_token = response.data.pop("refresh", None)

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
