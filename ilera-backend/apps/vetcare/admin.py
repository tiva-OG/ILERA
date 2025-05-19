from django.contrib import admin
from .models import CareSession, HealthRecord

admin.site.register(CareSession)
admin.site.register(HealthRecord)
