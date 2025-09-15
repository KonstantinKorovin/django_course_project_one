from django.contrib import admin

from users.models import Recipient


@admin.register(Recipient)
class AdminRecipient(admin.ModelAdmin):
    list_display = ("email", "full_name", "comment")
    list_filter = ("email", "full_name")
    search_fields = ("email", "full_name")
