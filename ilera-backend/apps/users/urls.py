from django.urls import path

from .views import UserSignupView, UserProfileView, CustomTokenObtainPairView, CustomTokenRefreshView, LogoutView

urlpatterns = [
    path("signup/", UserSignupView.as_view(), name="signup"),
    path("profile/", UserProfileView.as_view(), name="profile"),
    # authentication
    path("auth/login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/refresh-token/", CustomTokenRefreshView.as_view(), name="refresh-token"),
]
