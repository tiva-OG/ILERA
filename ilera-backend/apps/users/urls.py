from django.urls import path

from .views import (
    UserSignupView,
    UserOnboardingView,
    UserProfileView,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    LogoutView,
    VetListView,
    FarmerListView,
)

urlpatterns = [
    path("signup/", UserSignupView.as_view(), name="signup"),
    path("onboarding/", UserOnboardingView.as_view(), name="onboarding"),
    path("profile/", UserProfileView.as_view(), name="profile"),
    path("vet-list/", VetListView.as_view(), name="vet-list"),
    path("farmer-list/", FarmerListView.as_view(), name="farmer-list"),
    # authentication
    path("auth/login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/refresh-token/", CustomTokenRefreshView.as_view(), name="refresh-token"),
]
