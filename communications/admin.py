from django.contrib import admin

from communications.models import Message


@admin.register(Message)
class AdminMessage(admin.ModelAdmin):
    list_display = ("theme", "message")
    list_filter = ("theme", "message")
    search_fields = ("theme",)
