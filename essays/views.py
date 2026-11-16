import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count, F, Prefetch
from django.views import View
from django.views.generic import ListView, DetailView
from django.contrib.auth.views import redirect_to_login
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify as _slugify

from .models import Article, Tag
from . import images, services
from interactions.models import Comment, CommentLike
from interactions.services import get_hearted_ids


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


def _article_form(request) -> dict:
    """Article fields as posted, so the editor can be re-filled after an error."""
    return {
        "title": request.POST.get("title", "").strip(),
        "content": request.POST.get("content", "").strip(),
        "excerpt": request.POST.get("excerpt", "").strip(),
        "tag_names": request.POST.get("tag_names", ""),
    }


def _editor_error(request, template_name, message, form, essay=None):
    tags = [t for t in (name.strip() for name in form["tag_names"].split(",")) if t]
    context = {"error": message, "form_data": form, "existing_tags": json.dumps(tags)}
    if essay is not None:
        context["essay"] = essay
    return render(request, template_name, context)


def _processed_cover(request):
    """The uploaded cover, validated and re-encoded; None when no file was sent."""
    uploaded = request.FILES.get("cover_image")
    return images.process_upload(uploaded, images.COVER_MAX_SIZE) if uploaded else None


class EssayFeedView(LoginRequiredMixin, ListView):
    model = Article
    template_name = "essays/feed.html"
    context_object_name = "essays"
    paginate_by = 10

    def _feed(self):
        feed = self.request.GET.get("feed", services.FEED_FOR_YOU)
        if feed not in (services.FEED_FOR_YOU, services.FEED_FOLLOWING):
            feed = services.FEED_FOR_YOU
        return feed

    def _query(self):
        return self.request.GET.get("q", "").strip()[:100]

    def get_queryset(self):
        return services.get_home_feed(self.request.user, self._feed(), self._query())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["feed"] = self._feed()
        context["query"] = self._query()
        context["hearted_ids"] = get_hearted_ids(
            self.request.user, (essay.pk for essay in context["essays"])
        )
        return context


class EssayDetailView(DetailView):
    model = Article
    template_name = "essays/detail.html"
    context_object_name = "essay"

    def get_object(self, queryset=None):
        return get_object_or_404(
            Article.objects.select_related("author", "author__profile").prefetch_related(
                "tags"
            ),
            author__username=self.kwargs["username"],
            slug=self.kwargs["slug"],
            status=Article.PUBLISHED,
        )

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self._public_get(request)
        response = super().get(request, *args, **kwargs)
        self._record_view(request, self.object.pk)
        return response

    def _public_get(self, request):
        """Visitors who are not signed in may read public articles, and nothing else.

        Missing and members-only posts both send the visitor to sign in, so the
        response doesn't reveal whether a private article exists.
        """
        try:
            article = self.get_object()
        except Http404:
            article = None
        if article is None or not article.is_publicly_readable:
            return redirect_to_login(request.get_full_path())
        self._record_view(request, article.pk)
        return render(request, "essays/public_detail.html", {
            "essay": article,
            "heart_count": article.reactions.filter(reaction_type="heart").count(),
        })

    @staticmethod
    def _record_view(request, essay_pk):
        # Don't count the author visiting their own essay
        if (
            request.user.is_authenticated
            and Article.objects.filter(pk=essay_pk, author=request.user).exists()
        ):
            return
        # Deduplicate within a session
        seen_key = "seen_essays"
        seen = request.session.get(seen_key, [])
        if essay_pk in seen:
            return
        seen.append(essay_pk)
        request.session[seen_key] = seen
        Article.objects.filter(pk=essay_pk).update(view_count=F("view_count") + 1)

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
        context["comment_count"] = self.object.comments.count()
        context["is_hearted"] = False
        context["liked_comment_ids"] = set()
        if self.request.user.is_authenticated:
            context["is_hearted"] = self.object.reactions.filter(
                user=self.request.user, reaction_type="heart"
            ).exists()
            context["liked_comment_ids"] = set(
                CommentLike.objects.filter(
                    user=self.request.user, comment__article=self.object
                ).values_list("comment_id", flat=True)
            )
        return context


class EssayWriteView(LoginRequiredMixin, View):
    template_name = "essays/write.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        form = _article_form(request)
        action = request.POST.get("action", "draft")

        if not form["title"] or not form["content"]:
            return _editor_error(request, self.template_name, "Title and content are required.", form)
        try:
            cover = _processed_cover(request)
        except images.ImageRejected as e:
            return _editor_error(request, self.template_name, f"Cover image: {e}", form)

        essay = services.save_draft(
            request.user, form["title"], form["content"], excerpt=form["excerpt"]
        )
        _set_tags(essay, form["tag_names"])
        services.link_body_images(essay)
        if cover:
            services.set_cover(essay, cover)

        if action == "publish":
            services.publish_essay(essay)

        return redirect("accounts:profile", username=request.user.username)


class NoteCreateView(LoginRequiredMixin, View):
    """Post a short note: from the feed composer or the standalone note page."""

    template_name = "essays/note_new.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        content = request.POST.get("content", "")
        try:
            services.create_note(request.user, content)
        except ValueError as e:
            return render(request, self.template_name, {"error": str(e), "content": content})
        return redirect("essays:feed")


class EssayEditView(LoginRequiredMixin, View):
    template_name = "essays/edit.html"

    def _get_essay(self, request, username, slug):
        essay = get_object_or_404(Article, author__username=username, slug=slug)
        if essay.author != request.user:
            raise PermissionDenied
        return essay

    def get(self, request, username, slug):
        essay = self._get_essay(request, username, slug)
        if essay.is_note:
            return render(request, "essays/note_edit.html", {"essay": essay})
        existing_tags = json.dumps([tag.name for tag in essay.tags.all()])
        return render(
            request,
            self.template_name,
            {"essay": essay, "existing_tags": existing_tags},
        )

    def post(self, request, username, slug):
        essay = self._get_essay(request, username, slug)
        if essay.is_note:
            try:
                services.edit_note(essay, request.user, request.POST.get("content", ""))
            except ValueError as e:
                return render(
                    request,
                    "essays/note_edit.html",
                    {"essay": essay, "error": str(e), "content": request.POST.get("content", "")},
                )
            return redirect("essays:detail", username=essay.author.username, slug=essay.slug)
        action = request.POST.get("action", "save")

        if action == "publish":
            services.publish_essay(essay)
            return redirect(
                "essays:detail", username=essay.author.username, slug=essay.slug
            )

        if action == "unpublish":
            services.unpublish_essay(essay)
            return redirect("accounts:profile", username=request.user.username)

        form = _article_form(request)
        if not form["title"] or not form["content"]:
            return _editor_error(
                request, self.template_name, "Title and content are required.", form, essay
            )
        try:
            cover = _processed_cover(request)
        except images.ImageRejected as e:
            return _editor_error(request, self.template_name, f"Cover image: {e}", form, essay)

        services.edit_essay(
            essay, request.user, form["title"], form["content"], excerpt=form["excerpt"]
        )
        _set_tags(essay, form["tag_names"])
        services.link_body_images(essay)
        if cover:
            services.set_cover(essay, cover)
        elif request.POST.get("remove_cover") == "1":
            services.remove_cover(essay)

        if essay.status == Article.DRAFT:
            return redirect("accounts:profile", username=request.user.username)
        return redirect(
            "essays:detail", username=essay.author.username, slug=essay.slug
        )


class ImageUploadView(LoginRequiredMixin, View):
    """Upload endpoint for the article editor (EasyMDE): field `image`, JSON reply."""

    def post(self, request):
        uploaded = request.FILES.get("image")
        if not uploaded:
            return JsonResponse({"error": "noFileGiven"}, status=400)
        try:
            record = services.save_body_image(request.user, uploaded)
        except images.ImageRejected as e:
            return JsonResponse({"error": str(e)}, status=400)
        return JsonResponse({"data": {"filePath": record.image.url}})


class ArticleVisibilityView(LoginRequiredMixin, View):
    """The author shares an article publicly (`public=1`) or takes it back (`public=0`)."""

    def post(self, request, username, slug):
        article = get_object_or_404(Article, author__username=username, slug=slug)
        try:
            services.set_public(article, request.user, request.POST.get("public") == "1")
        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=400)
        return JsonResponse({"is_public": article.is_public})


class EssayDeleteView(LoginRequiredMixin, View):
    def post(self, request, username, slug):
        essay = get_object_or_404(Article, author__username=username, slug=slug)
        if essay.author != request.user:
            raise PermissionDenied
        services.remove_cover(essay)  # don't leave the cover file behind
        essay.delete()
        return redirect("accounts:profile", username=request.user.username)


class TagDetailView(DetailView):
    model = Tag
    template_name = "essays/tag.html"
    context_object_name = "tag"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        essays = list(
            services.with_engagement(
                self.object.articles.filter(status=Article.PUBLISHED)
                .select_related("author", "author__profile")
                .prefetch_related("tags")
                .order_by("-published_at")
            )
        )
        context["essays"] = essays
        context["hearted_ids"] = get_hearted_ids(
            self.request.user, (essay.pk for essay in essays)
        )
        return context
