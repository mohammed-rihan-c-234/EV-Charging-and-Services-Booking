from django.contrib import admin
from .models import ChargingStation

@admin.register(ChargingStation)
class ChargingStationAdmin(admin.ModelAdmin):
    list_display = ('name', 'available_slots')
    search_fields = ('name', 'address')
