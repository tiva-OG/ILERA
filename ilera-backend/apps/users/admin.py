from django.contrib import admin
from .models import User, FarmerProfile, VetProfile

admin.site.register(User)
admin.site.register(FarmerProfile)
admin.site.register(VetProfile)
