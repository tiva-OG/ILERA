import django_filters
from .models import Appointment


class AppointmentFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(field_name="scheduled_time", lookup_expr="gte")
    end_date = django_filters.DateFilter(field_name="scheduled_time", lookup_expr="lte")

    class Meta:
        model = Appointment
        fields = ["status", "vet", "farmer", "livestock", "start_date", "end_date"]
