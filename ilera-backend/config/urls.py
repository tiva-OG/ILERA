from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="ILERA API",
        default_version="v1.0",
        description="API documentation for the ILERA project",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@ilera.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("apps.users.urls")),
    path("api/v1/otp/", include("apps.otp.urls")),
    path("api/v1/sensors/", include("apps.sensors.urls")),
    path("api/v1/vetcare/", include("apps.vetcare.urls")),
    path("api/v1/livestock/", include("apps.livestock.urls")),
    path("api/v1/notifications/", include("apps.notifications.urls")),
    path("swagger/", schema_view.with_ui("swagger"), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc"), name="schema-redoc"),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
