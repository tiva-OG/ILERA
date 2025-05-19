from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CareRequestViewSet, CareSessionViewSet, HealthRecordViewSet

router = DefaultRouter()

router.register(r"requests", CareRequestViewSet)
router.register(r"sessions", CareSessionViewSet)
router.register(r"records", HealthRecordViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
