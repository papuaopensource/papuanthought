from django.conf import settings
from django.db import models


class Comment(models.Model):
    essay = models.ForeignKey(
        "essays.Essay", on_delete=models.CASCADE, related_name="comments"
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
        return f"Comment by {self.author} on {self.essay}"


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
        (HEART, "Heart"),
    ]

    essay = models.ForeignKey(
        "essays.Essay", on_delete=models.CASCADE, related_name="reactions"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reactions"
    )
    reaction_type = models.CharField(
        max_length=10, choices=REACTION_CHOICES, default=HEART
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("essay", "user", "reaction_type")

    def __str__(self):
        return f"{self.user} {self.reaction_type} on {self.essay}"


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


class Bookmark(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookmarks"
    )
    essay = models.ForeignKey(
        "essays.Essay", on_delete=models.CASCADE, related_name="bookmarks"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "essay")

    def __str__(self):
        return f"{self.user} bookmarked {self.essay}"


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
    essay = models.ForeignKey(
        "essays.Essay",
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
