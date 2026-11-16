from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.utils.functional import SimpleLazyObject


def sidebar_context(request):
    """
    Data for the app shell sidebars and follow buttons.

    Everything is lazy: queries only run when a template actually renders
    the value, so pages without sidebars (login, landing) don't pay for them.
    """
    from posts.models import Article
    from interactions.models import Follow, Report

    User = get_user_model()
    user = request.user
    published = Article.objects.filter(status=Article.PUBLISHED)
    published_articles = published.filter(kind=Article.ARTICLE)

    def following_ids():
        if not user.is_authenticated:
            return set()
        return set(
            Follow.objects.filter(follower=user).values_list("following_id", flat=True)
        )

    def following_list():
        if not user.is_authenticated:
            return []
        follows = (
            Follow.objects.filter(follower=user)
            .select_related("following", "following__profile")
            .order_by("-created_at")[:6]
        )
        return [follow.following for follow in follows]

    def suggested_writers():
        writers = (
            User.objects.filter(is_active=True)
            .annotate(
                published_count=Count(
                    "articles", filter=Q(articles__status=Article.PUBLISHED)
                )
            )
            .filter(published_count__gt=0)
            .select_related("profile")
        )
        if user.is_authenticated:
            writers = writers.exclude(pk=user.pk).exclude(
                pk__in=Follow.objects.filter(follower=user).values("following_id")
            )
        return list(writers.order_by("-published_count", "username")[:5])

    return {
        # Callables are resolved by the template engine only when rendered.
        "community_stats": {
            "essay_count": published_articles.count,
            "member_count": User.objects.filter(is_active=True).count,
        },
        "trending_essays": published_articles.select_related("author").order_by(
            "-view_count", "-published_at"
        )[:5],
        "following_ids": SimpleLazyObject(following_ids),
        "following_list": SimpleLazyObject(following_list),
        "suggested_writers": SimpleLazyObject(suggested_writers),
        "report_reasons": Report.REASON_CHOICES,
    }
