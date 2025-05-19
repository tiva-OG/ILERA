from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CareSessionViewSet, HealthRecordViewSet

router = DefaultRouter()

router.register(r"sessions", CareSessionViewSet, basename="sessions")
router.register(r"records", HealthRecordViewSet, basename="records")

urlpatterns = [
    path("", include(router.urls)),
]
