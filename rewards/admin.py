from django.contrib import admin
from .models import RewardAccount

@admin.register(RewardAccount)
class RewardAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'points', 'last_updated')
    search_fields = ('user__username',)
