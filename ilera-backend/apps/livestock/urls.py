from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import LivestockViewSet

router = DefaultRouter()
router.register(r"", LivestockViewSet, basename="livestock")

urlpatterns = router.urls
