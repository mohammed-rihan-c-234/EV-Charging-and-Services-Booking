from django.contrib import admin
from .models import SparePart, PartOrder, PartOrderItem

@admin.register(SparePart)
class SparePartAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'quantity', 'image_url')
    search_fields = ('name',)


class PartOrderItemInline(admin.TabularInline):
    model = PartOrderItem
    extra = 0
    readonly_fields = ("part", "quantity", "unit_price")


@admin.register(PartOrder)
class PartOrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "service_center", "status", "payment_status", "payment_method", "total_amount", "created_at")
    list_filter = ("status", "payment_status", "payment_method", "service_center")
    search_fields = ("user__username", "id")
    inlines = [PartOrderItemInline]
