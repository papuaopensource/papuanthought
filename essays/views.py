import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count, F, Prefetch
from django.views import View
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify as _slugify

from .models import Essay, Tag
from . import services
from interactions.models import Comment, CommentLike


def _set_tags(essay, tag_names_raw: str) -> None:
    tags = []
    for raw in tag_names_raw.split(","):
        name = raw.strip().lower()
        if name:
            tag, _ = Tag.objects.get_or_create(
                slug=_slugify(name), defaults={"name": name}
            )
            tags.append(tag)
    essay.tags.set(tags)


class EssayFeedView(LoginRequiredMixin, ListView):
    model = Essay
    template_name = "essays/feed.html"
    context_object_name = "essays"
    paginate_by = 10

    def get_queryset(self):
        return (
            Essay.objects.filter(status=Essay.PUBLISHED)
            .select_related("author", "author__profile")
            .prefetch_related("tags")
            .order_by("-published_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["featured"] = services.get_featured()
        return context


class EssayDetailView(DetailView):
    model = Essay
    template_name = "essays/detail.html"
    context_object_name = "essay"

    def get_object(self, queryset=None):
        return get_object_or_404(
            Essay.objects.select_related("author", "author__profile").prefetch_related(
                "tags"
            ),
            author__username=self.kwargs["username"],
            slug=self.kwargs["slug"],
            status=Essay.PUBLISHED,
        )

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        self._record_view(request, self.object.pk)
        return response

    @staticmethod
    def _record_view(request, essay_pk):
        # Don't count the author visiting their own essay
        if (
            request.user.is_authenticated
            and Essay.objects.filter(pk=essay_pk, author=request.user).exists()
        ):
            return
        # Deduplicate within a session
        seen_key = "seen_essays"
        seen = request.session.get(seen_key, [])
        if essay_pk in seen:
            return
        seen.append(essay_pk)
        request.session[seen_key] = seen
        Essay.objects.filter(pk=essay_pk).update(view_count=F("view_count") + 1)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        sort = self.request.GET.get("sort", "popular")
        if sort not in ("latest", "popular"):
            sort = "popular"

        replies_qs = (
            Comment.objects.annotate(like_count=Count("likes"))
            .select_related("author", "author__profile")
            .order_by("created_at")
        )
        comments_qs = (
            self.object.comments.filter(parent=None)
            .annotate(like_count=Count("likes"))
            .select_related("author", "author__profile")
            .prefetch_related(Prefetch("replies", queryset=replies_qs))
        )
        if sort == "popular":
            comments_qs = comments_qs.order_by("-like_count", "-created_at")
        else:
            comments_qs = comments_qs.order_by("-created_at")

        context["comments"] = comments_qs
        context["sort"] = sort

        context["heart_count"] = self.object.reactions.filter(
            reaction_type="heart"
        ).count()
        context["bookmark_count"] = self.object.bookmarks.count()
        context["is_hearted"] = False
        context["is_bookmarked"] = False
        context["liked_comment_ids"] = set()
        if self.request.user.is_authenticated:
            context["is_hearted"] = self.object.reactions.filter(
                user=self.request.user, reaction_type="heart"
            ).exists()
            context["is_bookmarked"] = self.object.bookmarks.filter(
                user=self.request.user
            ).exists()
            context["liked_comment_ids"] = set(
                CommentLike.objects.filter(
                    user=self.request.user, comment__essay=self.object
                ).values_list("comment_id", flat=True)
            )
        return context


class EssayWriteView(LoginRequiredMixin, View):
    template_name = "essays/write.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()
        excerpt = request.POST.get("excerpt", "").strip()
        action = request.POST.get("action", "draft")

        if not title or not content:
            return render(
                request,
                self.template_name,
                {"error": "Title and content are required."},
            )

        essay = services.save_draft(request.user, title, content, excerpt=excerpt)
        _set_tags(essay, request.POST.get("tag_names", ""))

        if action == "publish":
            services.publish_essay(essay)

        return redirect("accounts:profile", username=request.user.username)


class EssayEditView(LoginRequiredMixin, View):
    template_name = "essays/edit.html"

    def _get_essay(self, request, username, slug):
        essay = get_object_or_404(Essay, author__username=username, slug=slug)
        if essay.author != request.user:
            raise PermissionDenied
        return essay

    def get(self, request, username, slug):
        essay = self._get_essay(request, username, slug)
        existing_tags = json.dumps([tag.name for tag in essay.tags.all()])
        return render(
            request,
            self.template_name,
            {"essay": essay, "existing_tags": existing_tags},
        )

    def post(self, request, username, slug):
        essay = self._get_essay(request, username, slug)
        action = request.POST.get("action", "save")

        if action == "publish":
            services.publish_essay(essay)
            return redirect(
                "essays:detail", username=essay.author.username, slug=essay.slug
            )

        if action == "unpublish":
            services.unpublish_essay(essay)
            return redirect("accounts:profile", username=request.user.username)

        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()
        excerpt = request.POST.get("excerpt", "").strip()

        if not title or not content:
            existing_tags = json.dumps([tag.name for tag in essay.tags.all()])
            return render(
                request,
                self.template_name,
                {
                    "essay": essay,
                    "existing_tags": existing_tags,
                    "error": "Title and content are required.",
                },
            )

        services.edit_essay(essay, request.user, title, content, excerpt=excerpt)
        _set_tags(essay, request.POST.get("tag_names", ""))

        if essay.status == Essay.DRAFT:
            return redirect("accounts:profile", username=request.user.username)
        return redirect(
            "essays:detail", username=essay.author.username, slug=essay.slug
        )


class EssayDeleteView(LoginRequiredMixin, View):
    def post(self, request, username, slug):
        essay = get_object_or_404(Essay, author__username=username, slug=slug)
        if essay.author != request.user:
            raise PermissionDenied
        essay.delete()
        return redirect("accounts:profile", username=request.user.username)


class TagDetailView(DetailView):
    model = Tag
    template_name = "essays/tag.html"
    context_object_name = "tag"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["essays"] = (
            self.object.essays.filter(status=Essay.PUBLISHED)
            .select_related("author")
            .order_by("-published_at")
        )
        return context
