from django.contrib import admin

from mailings.models import Mailing, MailingAttempt


@admin.register(Mailing)
class AdminMailing(admin.ModelAdmin):
    list_display = (
        "first_date_mailing",
        "end_date_mailing",
        "status",
    )
    list_filter = ("first_date_mailing", "end_date_mailing", "status", "recipients")
    search_fields = ("status", "recipients")


@admin.register(MailingAttempt)
class AdminMailingAttempt(admin.ModelAdmin):
    list_display = ("date_attempt", "status", "response_status", "mailing")
    list_filter = ("date_attempt", "status", "response_status", "mailing")
    search_fields = ("status", "response_status", "mailing")
