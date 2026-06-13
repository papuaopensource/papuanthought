from django.core.exceptions import PermissionDenied

from .models import Comment, CommentLike, Reaction, Follow, Bookmark, Notification


def add_comment(essay, author, content: str, parent=None, quote=None) -> Comment:
    comment = Comment.objects.create(
        essay=essay,
        author=author,
        content=content,
        parent=parent,
        quote=quote or None,
    )
    if essay.author != author:
        Notification.objects.create(
            recipient=essay.author,
            sender=author,
            notification_type=Notification.COMMENT,
            essay=essay,
        )
    return comment


def edit_comment(comment: Comment, user, content: str) -> Comment:
    if comment.author != user:
        raise PermissionDenied
    comment.content = content.strip()
    comment.is_edited = True
    comment.save(update_fields=["content", "is_edited", "updated_at"])
    return comment


def toggle_comment_like(comment: Comment, user) -> CommentLike | None:
    like, created = CommentLike.objects.get_or_create(comment=comment, user=user)
    if not created:
        like.delete()
        return None
    return like


def delete_comment(comment: Comment, user) -> None:
    if comment.author != user:
        raise PermissionDenied
    comment.delete()


def toggle_reaction(essay, user, reaction_type: str) -> Reaction | None:
    reaction, created = Reaction.objects.get_or_create(
        essay=essay,
        user=user,
        reaction_type=reaction_type,
    )
    if not created:
        reaction.delete()
        return None
    if essay.author != user:
        Notification.objects.create(
            recipient=essay.author,
            sender=user,
            notification_type=Notification.REACTION,
            essay=essay,
        )
    return reaction


def follow_user(follower, target) -> Follow | None:
    if follower == target:
        return None
    follow, created = Follow.objects.get_or_create(
        follower=follower,
        following=target,
    )
    if not created:
        follow.delete()
        return None
    Notification.objects.create(
        recipient=target,
        sender=follower,
        notification_type=Notification.FOLLOW,
    )
    return follow


def toggle_bookmark(user, essay) -> Bookmark | None:
    bookmark, created = Bookmark.objects.get_or_create(user=user, essay=essay)
    if not created:
        bookmark.delete()
        return None
    return bookmark


def notify_new_essay(essay) -> None:
    followers = Follow.objects.filter(following=essay.author).select_related("follower")
    batch = [
        Notification(
            recipient=f.follower,
            sender=essay.author,
            notification_type=Notification.NEW_POST,
            essay=essay,
        )
        for f in followers
    ]
    if batch:
        Notification.objects.bulk_create(batch)


def create_recommendations(essay) -> None:
    from accounts.models import User
    following_ids = Follow.objects.filter(
        following=essay.author
    ).values_list("follower_id", flat=True)
    already_notified = Notification.objects.filter(
        essay=essay, notification_type=Notification.RECOMMEND
    ).values_list("recipient_id", flat=True)
    users = (
        User.objects.exclude(pk=essay.author.pk)
        .exclude(pk__in=following_ids)
        .exclude(pk__in=already_notified)
    )
    batch = [
        Notification(
            recipient=user,
            notification_type=Notification.RECOMMEND,
            essay=essay,
        )
        for user in users
    ]
    if batch:
        Notification.objects.bulk_create(batch)
