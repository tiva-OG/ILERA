from rest_framework.routers import DefaultRouter

from .views import AppointmentViewSet

router = DefaultRouter()
router.register(r"", AppointmentViewSet, basename="appointments")

urlpatterns = router.urls

# method        URL                     action
# GET         /appointments/          list appointments
# POST        /appointments/          create new appointment
# GET         /appointments/{id}/     retrieve appointment
# PATCH       /appointments/{id}/     partial update appointment
# PUT         /appointments/{id}/     full update appointment
# DELETE       /appointments/{id}/    delete (cancel) appointment
