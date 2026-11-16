from django.conf import settings
from django.db import models


class Comment(models.Model):
    article = models.ForeignKey(
        "posts.Article", on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )
    content = models.TextField()
    quote = models.TextField(blank=True, null=True)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="replies",
    )
    is_edited = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.author} on {self.article}"


class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comment_likes"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("comment", "user")

    def __str__(self):
        return f"{self.user} liked comment {self.comment_id}"


class Reaction(models.Model):
    HEART = "heart"
    REACTION_CHOICES = [
        (HEART, "Like"),  # stored as "heart"; shown as a like (heart icon)
    ]

    article = models.ForeignKey(
        "posts.Article", on_delete=models.CASCADE, related_name="reactions"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reactions"
    )
    reaction_type = models.CharField(
        max_length=10, choices=REACTION_CHOICES, default=HEART
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("article", "user", "reaction_type")

    def __str__(self):
        return f"{self.user} {self.reaction_type} on {self.article}"


class Follow(models.Model):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="following"
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="followers"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "following")

    def __str__(self):
        return f"{self.follower} → {self.following}"


class Notification(models.Model):
    COMMENT = "comment"
    REACTION = "reaction"
    FOLLOW = "follow"
    NEW_POST = "new_post"
    RECOMMEND = "recommend"
    TYPE_CHOICES = [
        (COMMENT, "Comment"),
        (REACTION, "Reaction"),
        (FOLLOW, "Follow"),
        (NEW_POST, "New Post"),
        (RECOMMEND, "Recommendation"),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_notifications",
    )
    notification_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    article = models.ForeignKey(
        "posts.Article",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Notification({self.notification_type}) → {self.recipient}"


class Report(models.Model):
    """A member flagging an article/note, a comment, or another member's profile for admin review."""

    SPAM = "spam"
    HARASSMENT = "harassment"
    HATE = "hate"
    MISINFORMATION = "misinformation"
    PLAGIARISM = "plagiarism"
    IMPERSONATION = "impersonation"
    INAPPROPRIATE = "inappropriate"
    OTHER = "other"
    REASON_CHOICES = [
        (SPAM, "Spam or self-promotion"),
        (HARASSMENT, "Harassment or bullying"),
        (HATE, "Hate speech"),
        (MISINFORMATION, "False or misleading information"),
        (PLAGIARISM, "Plagiarism or stolen content"),
        (IMPERSONATION, "Impersonation or fake account"),
        (INAPPROPRIATE, "Inappropriate or harmful content"),
        (OTHER, "Something else"),
    ]

    OPEN = "open"
    REVIEWED = "reviewed"
    DISMISSED = "dismissed"
    STATUS_CHOICES = [
        (OPEN, "Open"),
        (REVIEWED, "Reviewed"),
        (DISMISSED, "Dismissed"),
    ]

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reports_made",
    )
    article = models.ForeignKey(
        "posts.Article",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="reports",
    )
    reported_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="reports_received",
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="reports",
    )
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    details = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            # Every report targets exactly one thing: an essay, a comment or a profile.
            models.CheckConstraint(
                condition=(
                    models.Q(article__isnull=False, comment__isnull=True, reported_user__isnull=True)
                    | models.Q(article__isnull=True, comment__isnull=False, reported_user__isnull=True)
                    | models.Q(article__isnull=True, comment__isnull=True, reported_user__isnull=False)
                ),
                name="report_single_target",
            ),
        ]

    def __str__(self):
        if self.article_id:
            target = f"{self.article.get_kind_display().lower()} “{self.article}”"
        elif self.comment_id:
            target = f"comment #{self.comment_id}"
        else:
            target = f"user @{self.reported_user}"
        return f"Report on {target} by {self.reporter}"
