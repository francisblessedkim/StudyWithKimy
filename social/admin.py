from django.contrib import admin
from .models import StatusUpdate, Notification

@admin.register(StatusUpdate)
class StatusUpdateAdmin(admin.ModelAdmin):
    list_display = ("author", "text", "created_at")
    search_fields = ("author__username", "text")

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("recipient", "type", "is_read", "created_at")
    list_filter = ("type", "is_read")
