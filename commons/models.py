from django.conf import settings
from django.db import models


class Feedback(models.Model):
    """Feedback a member sends to the team: ideas, bug reports, questions."""

    IDEA = "idea"
    BUG = "bug"
    QUESTION = "question"
    OTHER = "other"
    CATEGORY_CHOICES = [
        (IDEA, "Idea"),
        (BUG, "Bug"),
        (QUESTION, "Question"),
        (OTHER, "Other"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="feedback",
    )
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default=OTHER)
    # Snapshot of the sender, so feedback stays readable if the account is deleted.
    name = models.CharField(max_length=150)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "feedback"
        verbose_name_plural = "feedback"

    def __str__(self):
        return f"{self.get_category_display()} from {self.name} — {self.created_at:%Y-%m-%d}"
