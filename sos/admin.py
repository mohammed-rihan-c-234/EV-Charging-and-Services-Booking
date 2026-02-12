from django.contrib import admin
from .models import SOSAlert, AssignedCenter

@admin.register(SOSAlert)
class SOSAlertAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'vehicle', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'vehicle__owner_name')


@admin.register(AssignedCenter)
class AssignedCenterAdmin(admin.ModelAdmin):
    list_display = ('id', 'alert', 'center', 'distance_km', 'assigned_at')
    list_filter = ('assigned_at', 'center')
    search_fields = ('alert__id', 'center__name')
