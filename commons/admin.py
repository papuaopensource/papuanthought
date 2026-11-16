from django.contrib import admin
from django.utils.text import Truncator
from unfold.admin import ModelAdmin

from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(ModelAdmin):
    list_display = ("category", "name", "message_preview", "created_at", "is_read")
    list_filter = ("category", "is_read")
    search_fields = ("name", "email", "message")
    readonly_fields = ("user", "category", "name", "email", "message", "created_at")
    fields = ("category", "message", "user", "name", "email", "created_at", "is_read")
    list_editable = ("is_read",)
    ordering = ("-created_at",)

    def has_add_permission(self, request):
        return False  # feedback comes from members on the site

    @admin.display(description="Message")
    def message_preview(self, obj):
        return Truncator(obj.message).chars(80)
