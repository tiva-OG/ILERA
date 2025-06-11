from django.urls import path
from .views import SensorReadingListCreateView

urlpatterns = [
    path("", SensorReadingListCreateView.as_view(), name="sensors"),
]
