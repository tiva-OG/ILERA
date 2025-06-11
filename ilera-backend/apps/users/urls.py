from django.urls import path

from .views import (
    UserSignupView,
    UserVerifyOTPView,
    UserOnboardingView,
    UserProfileView,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    LogoutView,
    VetListView,
    VetDetailView,
    FarmerListView,
    FarmerDetailView,
)

urlpatterns = [
    path("signup/", UserSignupView.as_view(), name="signup"),
    path("verify-otp/", UserVerifyOTPView.as_view(), name="verify-otp"),
    path("onboarding/", UserOnboardingView.as_view(), name="onboarding"),
    path("profile/", UserProfileView.as_view(), name="profile"),
    path("farmer-list/", FarmerListView.as_view(), name="farmer-list"),
    path("farmer-detail/<str:farmer_id>/", FarmerDetailView.as_view(), name="farmer-detail"),
    path("vet-list/", VetListView.as_view(), name="vet-list"),
    path("vet-detail/<str:vet_id>/", VetDetailView.as_view(), name="vet-detail"),
    # authentication
    path("auth/login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/refresh-token/", CustomTokenRefreshView.as_view(), name="refresh-token"),
]
