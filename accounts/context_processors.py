from django.contrib.auth import get_user_model


def sidebar_context(request):
    from essays.models import Essay

    User = get_user_model()

    member_count = User.objects.filter(is_active=True).count()
    essay_count = Essay.objects.filter(status=Essay.PUBLISHED).count()

    trending = (
        Essay.objects.filter(status=Essay.PUBLISHED)
        .select_related("author")
        .order_by("-view_count", "-published_at")[:5]
    )

    return {
        "community_stats": {
            "essay_count": essay_count,
            "member_count": member_count,
        },
        "trending_essays": trending,
    }
