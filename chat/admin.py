from django.contrib import admin
from .models import ChatMessage

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("sender", "receiver", "message", "timestamp")
    search_fields = ("sender__username", "receiver__username", "message")
    list_filter = ("timestamp",)
