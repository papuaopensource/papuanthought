from django.core.exceptions import PermissionDenied

from .models import Comment, CommentLike, Reaction, Follow, Notification, Report


def add_comment(essay, author, content: str, parent=None, quote=None) -> Comment:
    comment = Comment.objects.create(
        article=essay,
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
            article=essay,
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
        article=essay,
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
            article=essay,
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


def notify_new_essay(essay) -> None:
    followers = Follow.objects.filter(following=essay.author).select_related("follower")
    batch = [
        Notification(
            recipient=f.follower,
            sender=essay.author,
            notification_type=Notification.NEW_POST,
            article=essay,
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
        article=essay, notification_type=Notification.RECOMMEND
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
            article=essay,
        )
        for user in users
    ]
    if batch:
        Notification.objects.bulk_create(batch)


def get_hearted_ids(user, essay_ids) -> set[int]:
    """IDs among `essay_ids` that `user` has liked."""
    if not user.is_authenticated:
        return set()
    return set(
        Reaction.objects.filter(
            user=user, article_id__in=list(essay_ids), reaction_type=Reaction.HEART
        ).values_list("article_id", flat=True)
    )


def submit_report(
    reporter, *, reason: str, details: str = "", article=None, comment=None, user=None
) -> Report:
    """File a report on a post (article or note), a comment or a member profile.

    A second report from the same member on the same target, while the first is
    still open, updates that report instead of adding a duplicate.
    """
    targets = [t for t in (article, comment, user) if t is not None]
    if len(targets) != 1:
        raise ValueError("Report exactly one post, comment or member.")
    if reason not in dict(Report.REASON_CHOICES):
        raise ValueError("Choose a reason for the report.")
    if article is not None:
        target_owner = article.author
    elif comment is not None:
        target_owner = comment.author
    else:
        target_owner = user
    if target_owner == reporter:
        raise ValueError("You can't report your own content or profile.")

    details = details.strip()[:2000]
    report, created = Report.objects.get_or_create(
        reporter=reporter,
        article=article,
        comment=comment,
        reported_user=user,
        status=Report.OPEN,
        defaults={"reason": reason, "details": details},
    )
    if not created:
        report.reason = reason
        report.details = details
        report.save(update_fields=["reason", "details", "updated_at"])
    return report
