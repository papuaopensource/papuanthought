from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from essays.models import Essay
from accounts.models import User
from .models import Comment, CommentLike, Notification
from . import services


class CommentCreateView(LoginRequiredMixin, View):
    def post(self, request, essay_id):
        essay = get_object_or_404(Essay, pk=essay_id, status=Essay.PUBLISHED)
        content = request.POST.get("content", "").strip()
        parent_id = request.POST.get("parent_id")
        quote = request.POST.get("quote", "").strip() or None
        parent = None
        if parent_id:
            parent = get_object_or_404(Comment, pk=parent_id, essay=essay)
        if content:
            services.add_comment(essay, request.user, content, parent=parent, quote=quote)
        return redirect("essays:detail", username=essay.author.username, slug=essay.slug)


class CommentEditView(LoginRequiredMixin, View):
    template_name = "interactions/comment_edit.html"

    def _get_comment(self, request, comment_id):
        comment = get_object_or_404(Comment, pk=comment_id)
        if comment.author != request.user:
            raise PermissionDenied
        return comment

    def get(self, request, comment_id):
        comment = self._get_comment(request, comment_id)
        return render(request, self.template_name, {"comment": comment})

    def post(self, request, comment_id):
        comment = self._get_comment(request, comment_id)
        content = request.POST.get("content", "").strip()
        if content:
            services.edit_comment(comment, request.user, content)
        essay = comment.essay
        return redirect("essays:detail", username=essay.author.username, slug=essay.slug)


class CommentDeleteView(LoginRequiredMixin, View):
    def post(self, request, comment_id):
        comment = get_object_or_404(Comment, pk=comment_id)
        essay = comment.essay
        services.delete_comment(comment, request.user)
        return redirect("essays:detail", username=essay.author.username, slug=essay.slug)


class ReactionToggleView(LoginRequiredMixin, View):
    def post(self, request, essay_id):
        essay = get_object_or_404(Essay, pk=essay_id, status=Essay.PUBLISHED)
        reaction_type = request.POST.get("reaction_type", "heart")
        result = services.toggle_reaction(essay, request.user, reaction_type)
        return JsonResponse({"reacted": result is not None})


class FollowToggleView(LoginRequiredMixin, View):
    def post(self, request, username):
        target = get_object_or_404(User, username=username)
        result = services.follow_user(request.user, target)
        return JsonResponse({"following": result is not None})


class BookmarkToggleView(LoginRequiredMixin, View):
    def post(self, request, essay_id):
        essay = get_object_or_404(Essay, pk=essay_id, status=Essay.PUBLISHED)
        result = services.toggle_bookmark(request.user, essay)
        return JsonResponse({"bookmarked": result is not None})


class CommentLikeToggleView(LoginRequiredMixin, View):
    def post(self, request, comment_id):
        comment = get_object_or_404(Comment, pk=comment_id)
        result = services.toggle_comment_like(comment, request.user)
        count = comment.likes.count()
        return JsonResponse({"liked": result is not None, "count": count})


class NotificationListView(LoginRequiredMixin, View):
    template_name = "interactions/notifications.html"

    def get(self, request):
        notifications = list(
            Notification.objects.filter(recipient=request.user)
            .select_related("sender", "sender__profile", "essay", "essay__author")
            .order_by("-created_at")[:50]
        )
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return render(request, self.template_name, {"notifications": notifications})
