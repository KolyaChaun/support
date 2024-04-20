from django.contrib import admin

from .models import Issue, Message


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    readonly_fields = [
        "junior",
        "senior",
    ]
    list_display = ["id", "title", "junior", "senior"]


# TO DO
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    pass
