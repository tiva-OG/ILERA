from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("apps.users.urls")),
    path("api/v1/otp/", include("apps.otp.urls")),
    path("api/v1/sensor/", include("apps.sensors.urls")),
    path("api/v1/vetcare/", include("apps.vetcare.urls")),
    path("api/v1/livestock/", include("apps.livestock.urls")),
]
