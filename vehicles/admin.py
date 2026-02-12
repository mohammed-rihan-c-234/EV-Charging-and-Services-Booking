from django.contrib import admin
from .models import Vehicle

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('owner_name', 'make', 'model', 'year', 'license_plate')
    search_fields = ('owner_name', 'make', 'model', 'license_plate')
