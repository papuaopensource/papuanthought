from django.utils import timezone
from django.core.paginator import Paginator

from .models import Essay


def get_feed(page: int = 1, per_page: int = 10):
    qs = (
        Essay.objects.filter(status=Essay.PUBLISHED)
        .select_related("author", "author__profile")
        .prefetch_related("categories", "tags")
        .order_by("-published_at")
    )
    return Paginator(qs, per_page).get_page(page)


def get_featured():
    return (
        Essay.objects.filter(status=Essay.PUBLISHED, is_featured=True)
        .select_related("author")
        .order_by("-published_at")[:5]
    )


def save_draft(author, title: str, content: str, **kwargs) -> Essay:
    return Essay.objects.create(
        author=author,
        title=title,
        content=content,
        status=Essay.DRAFT,
        **kwargs,
    )


def publish_essay(essay: Essay) -> Essay:
    essay.status = Essay.PUBLISHED
    essay.published_at = timezone.now()
    essay.save(update_fields=["status", "published_at"])
    from interactions.services import notify_new_essay, create_recommendations
    notify_new_essay(essay)
    if essay.is_featured:
        create_recommendations(essay)
    return essay


def edit_essay(essay: Essay, user, title: str, content: str, excerpt: str = "") -> Essay:
    from django.core.exceptions import PermissionDenied
    if essay.author != user:
        raise PermissionDenied
    essay.title = title
    essay.content = content
    essay.excerpt = excerpt
    essay.read_time = max(1, round(len(content.split()) / 200))
    if essay.status == Essay.PUBLISHED:
        essay.is_edited = True
    essay.save(update_fields=["title", "content", "excerpt", "read_time", "is_edited"])
    return essay


def unpublish_essay(essay: Essay) -> Essay:
    essay.status = Essay.DRAFT
    essay.save(update_fields=["status"])
    return essay


def archive_essay(essay: Essay) -> Essay:
    essay.status = Essay.ARCHIVED
    essay.save(update_fields=["status"])
    return essay
