from django.contrib import admin, messages
from django.urls import reverse
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.decorators import action, display

from .models import Comment, Reaction, Follow, Notification, Report



@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ("author", "article", "parent", "created_at")
    search_fields = ("author__username", "content", "article__title")
    raw_id_fields = ("article", "author", "parent")


@admin.register(Reaction)
class ReactionAdmin(ModelAdmin):
    list_display = ("user", "article", "reaction_type", "created_at")
    list_filter = ("reaction_type",)
    raw_id_fields = ("article", "user")


@admin.register(Follow)
class FollowAdmin(ModelAdmin):
    list_display = ("follower", "following", "created_at")
    raw_id_fields = ("follower", "following")


@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    list_display = ("recipient", "sender", "notification_type", "is_read", "created_at")
    list_filter = ("notification_type", "is_read")
    raw_id_fields = ("recipient", "sender", "article")


@admin.register(Report)
class ReportAdmin(ModelAdmin):
    list_display = ("target_display", "reason", "reporter", "status_display", "created_at")
    list_filter = ("status", "reason", "created_at")
    search_fields = (
        "details",
        "reporter__username",
        "reported_user__username",
        "article__title",
        "article__author__username",
        "comment__content",
        "comment__author__username",
    )
    readonly_fields = (
        "reporter", "article", "comment", "comment_text", "reported_user",
        "reason", "details", "created_at", "updated_at",
    )
    fields = (
        "status", "reason", "details", "article", "comment", "comment_text",
        "reported_user", "reporter", "created_at", "updated_at",
    )
    list_select_related = (
        "reporter", "article", "article__author", "reported_user",
        "comment", "comment__author", "comment__article", "comment__article__author",
    )
    actions = ["mark_reviewed", "mark_dismissed"]

    def has_add_permission(self, request):
        return False  # reports come from members on the site

    @display(description="Reported")
    def target_display(self, obj):
        if obj.article_id:
            url = reverse("posts:detail", kwargs={"username": obj.article.author.username, "slug": obj.article.slug})
            return format_html('{}: <a href="{}" target="_blank" rel="noopener">{}</a>', obj.article.get_kind_display(), url, obj.article.display_title)
        if obj.comment_id:
            essay = obj.comment.article
            url = reverse("posts:detail", kwargs={"username": essay.author.username, "slug": essay.slug})
            return format_html(
                'Comment by @{} on <a href="{}#comment-{}" target="_blank" rel="noopener">{}</a>',
                obj.comment.author.username, url, obj.comment_id, essay.display_title,
            )
        url = reverse("accounts:profile", kwargs={"username": obj.reported_user.username})
        return format_html('Profile: <a href="{}" target="_blank" rel="noopener">@{}</a>', url, obj.reported_user.username)

    @display(description="Comment text")
    def comment_text(self, obj):
        return obj.comment.content if obj.comment_id else "—"

    @display(
        description="Status",
        label={Report.OPEN: "warning", Report.REVIEWED: "success", Report.DISMISSED: "info"},
    )
    def status_display(self, obj):
        return obj.status, obj.get_status_display()

    @action(description="Mark selected reports as reviewed")
    def mark_reviewed(self, request, queryset):
        updated = queryset.update(status=Report.REVIEWED)
        self.message_user(request, f"{updated} report(s) marked as reviewed.", messages.SUCCESS)

    @action(description="Dismiss selected reports")
    def mark_dismissed(self, request, queryset):
        updated = queryset.update(status=Report.DISMISSED)
        self.message_user(request, f"{updated} report(s) dismissed.", messages.SUCCESS)
