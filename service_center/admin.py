from django.contrib import admin
from .models import ServiceCenter

@admin.register(ServiceCenter)
class ServiceCenterAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone')
    search_fields = ('name', 'address')
