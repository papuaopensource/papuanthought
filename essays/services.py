import re

from django.db.models import Count, IntegerField, OuterRef, Q, Subquery
from django.db.models.functions import Coalesce
from django.utils import timezone

from .models import Article

FEED_FOR_YOU = "for-you"
FEED_FOLLOWING = "following"


def _count_of(model, **filters):
    """Correlated COUNT(*) subquery of `model` rows pointing at the outer essay."""
    counts = (
        model.objects.filter(article=OuterRef("pk"), **filters)
        .order_by()
        .values("article")
        .annotate(n=Count("pk"))
        .values("n")
    )
    return Coalesce(Subquery(counts, output_field=IntegerField()), 0)


def with_engagement(queryset):
    """Annotate essays with `heart_count` and `comment_count` for feed cards."""
    from interactions.models import Comment, Reaction

    return queryset.annotate(
        heart_count=_count_of(Reaction, reaction_type=Reaction.HEART),
        comment_count=_count_of(Comment),
    )


def get_home_feed(user, feed: str = FEED_FOR_YOU, query: str = ""):
    """Published essays for the home feed, newest first.

    `feed` narrows to authors `user` follows; `query` searches title, subtitle,
    body, tags and author names.
    """
    qs = Article.objects.filter(status=Article.PUBLISHED)
    if feed == FEED_FOLLOWING and user.is_authenticated:
        from interactions.models import Follow

        qs = qs.filter(
            author__in=Follow.objects.filter(follower=user).values("following")
        )
    if query:
        matches = Article.objects.filter(
            Q(title__icontains=query)
            | Q(excerpt__icontains=query)
            | Q(content__icontains=query)
            | Q(tags__name__icontains=query)
            | Q(author__username__icontains=query)
            | Q(author__first_name__icontains=query)
            | Q(author__last_name__icontains=query)
        ).values("pk")
        qs = qs.filter(pk__in=matches)
    return with_engagement(
        qs.select_related("author", "author__profile")
        .prefetch_related("tags")
        .order_by("-published_at")
    )


def get_liked_by(user):
    """Published essays `user` has liked, most recently liked first."""
    from interactions.models import Reaction

    liked_at = Reaction.objects.filter(
        article=OuterRef("pk"), user=user, reaction_type=Reaction.HEART
    ).values("created_at")[:1]
    return with_engagement(
        Article.objects.filter(status=Article.PUBLISHED)
        .annotate(liked_at=Subquery(liked_at))
        .filter(liked_at__isnull=False)
        .select_related("author", "author__profile")
        .prefetch_related("tags")
        .order_by("-liked_at")
    )


def set_cover(essay: Article, content) -> Article:
    """Attach an already-processed cover (see essays.images), replacing any old file."""
    old_name = essay.cover_image.name if essay.cover_image else ""
    essay.cover_image.save(content.name, content, save=False)
    essay.save(update_fields=["cover_image"])
    if old_name:
        essay.cover_image.storage.delete(old_name)
    return essay


def remove_cover(essay: Article) -> Article:
    if essay.cover_image:
        essay.cover_image.delete(save=False)
        essay.save(update_fields=["cover_image"])
    return essay


def save_body_image(uploader, uploaded):
    """Store an image uploaded from the article editor; returns the ArticleImage."""
    from .images import process_upload
    from .models import ArticleImage

    content = process_upload(uploaded)
    record = ArticleImage(uploader=uploader)
    record.image.save(content.name, content, save=True)
    return record


_MARKDOWN_IMAGE_URL = re.compile(r"!\[[^\]]*\]\(\s*<?([^)\s>]+)")


def link_body_images(article: Article) -> None:
    """Attach the author's uploaded images to the article whose body uses them.

    Images no longer referenced by this article are detached (kept as uploads).
    """
    from .models import ArticleImage

    used = set(_MARKDOWN_IMAGE_URL.findall(article.content or ""))
    candidates = ArticleImage.objects.filter(uploader=article.author).filter(
        Q(article__isnull=True) | Q(article=article)
    )
    for image in candidates:
        should_link = image.image.url in used
        if should_link and image.article_id != article.pk:
            image.article = article
            image.save(update_fields=["article"])
        elif not should_link and image.article_id == article.pk:
            image.article = None
            image.save(update_fields=["article"])


def _clean_note(content: str) -> str:
    content = content.strip()
    if not content:
        raise ValueError("Write something first.")
    if len(content) > Article.NOTE_MAX_LENGTH:
        raise ValueError(f"Notes can be up to {Article.NOTE_MAX_LENGTH} characters.")
    return content


def create_note(author, content: str) -> Article:
    """Post a short note. Notes skip drafts and go live (and notify followers) at once."""
    note = Article.objects.create(
        author=author,
        kind=Article.NOTE,
        content=_clean_note(content),
        status=Article.DRAFT,
    )
    return publish_essay(note)


def edit_note(note: Article, user, content: str) -> Article:
    from django.core.exceptions import PermissionDenied
    if note.author != user:
        raise PermissionDenied
    note.content = _clean_note(content)
    note.read_time = max(1, round(len(note.content.split()) / 200))
    note.is_edited = True
    note.save(update_fields=["content", "read_time", "is_edited"])
    return note


def save_draft(author, title: str, content: str, **kwargs) -> Article:
    return Article.objects.create(
        author=author,
        title=title,
        content=content,
        status=Article.DRAFT,
        **kwargs,
    )


def publish_essay(essay: Article) -> Article:
    essay.status = Article.PUBLISHED
    essay.published_at = timezone.now()
    essay.save(update_fields=["status", "published_at"])
    from interactions.services import notify_new_essay, create_recommendations
    notify_new_essay(essay)
    if essay.is_featured:
        create_recommendations(essay)
    return essay


def edit_essay(essay: Article, user, title: str, content: str, excerpt: str = "") -> Article:
    from django.core.exceptions import PermissionDenied
    if essay.author != user:
        raise PermissionDenied
    essay.title = title
    essay.content = content
    essay.excerpt = excerpt
    essay.read_time = max(1, round(len(content.split()) / 200))
    if essay.status == Article.PUBLISHED:
        essay.is_edited = True
    essay.save(update_fields=["title", "content", "excerpt", "read_time", "is_edited"])
    return essay


def unpublish_essay(essay: Article) -> Article:
    essay.status = Article.DRAFT
    essay.is_public = False  # a draft is never public; sharing must be turned on again
    essay.save(update_fields=["status", "is_public"])
    return essay


def set_public(article: Article, user, public: bool) -> Article:
    """Share a published article with everyone (or take it back). Author only."""
    from django.core.exceptions import PermissionDenied

    if article.author != user:
        raise PermissionDenied
    if article.kind != Article.ARTICLE:
        raise ValueError("Only articles can be shared publicly.")
    if public and article.status != Article.PUBLISHED:
        raise ValueError("Publish the article before sharing it publicly.")
    article.is_public = public
    article.save(update_fields=["is_public"])
    return article


def archive_essay(essay: Article) -> Article:
    essay.status = Article.ARCHIVED
    essay.save(update_fields=["status"])
    return essay
