from django.contrib.auth import get_user_model


def community_members(request):
    User = get_user_model()
    members = (
        User.objects.filter(is_active=True)
        .select_related("profile")
        .order_by("-date_joined")[:8]
    )
    return {"community_members": members}
