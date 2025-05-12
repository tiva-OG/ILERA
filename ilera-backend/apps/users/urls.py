from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView
from django.urls import path

from .views import UserSignupView, UserProfileView, CustomObtainTokenPairView

urlpatterns = [
    path("signup/", UserSignupView.as_view(), name="signup"),
    path("profile/", UserProfileView.as_view(), name="profile"),
    # authentication
    path("auth/login/", CustomObtainTokenPairView.as_view(), name="login"),
    path("auth/logout/", TokenBlacklistView.as_view(), name="logout"),
    path("auth/refresh-token/", TokenRefreshView.as_view(), name="refresh-token"),
]
