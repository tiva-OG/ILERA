from rest_framework import generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User
from .serializers import UserSignupSerializer, UserProfileSerializer, CustomObtainTokenPairSerializer


# ========================================== Create new user ==========================================
class UserSignupView(generics.CreateAPIView):
    serializer_class = UserSignupSerializer
    permission_classes = [permissions.AllowAny]


# ========================================== View user profile ==========================================
class UserProfileView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


# ========================================== Obtain token on login ==========================================
class CustomObtainTokenPairView(TokenObtainPairView):
    serializer_class = CustomObtainTokenPairSerializer
