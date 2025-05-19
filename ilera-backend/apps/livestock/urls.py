from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import LivestockListCreateView, LivestockDeleteView, LivestockArchiveView, LivestockViewSet

router = DefaultRouter()
router.register(r"livestock2", LivestockViewSet, basename="livestock2")

urlpatterns = [
    path("l2/", include(router.urls)),
    path("", LivestockListCreateView.as_view(), name="livestock-list-create"),
    path("<uuid:pk>/delete/", LivestockDeleteView.as_view(), name="livestock-delete"),
    path("<uuid:pk>/archive/", LivestockArchiveView.as_view(), name="livestock-archive"),
]
