import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    email = models.EmailField(_("email address"), unique=True)

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return self.username


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile"
    )
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to="profiles/", blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    twitter = models.CharField(max_length=50, blank=True)
    instagram = models.CharField(max_length=50, blank=True)
    motivation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.username}"


class Invitation(models.Model):
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    note = models.CharField(
        max_length=120,
        blank=True,
        help_text="Optional internal label, e.g. 'for John from Twitter'.",
    )
    invited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="invitations_sent",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def is_used(self):
        return self.used_at is not None

    @property
    def accept_path(self):
        from django.urls import reverse
        return reverse("accounts:invitation_accept", kwargs={"token": self.token})

    def __str__(self):
        return self.note or str(self.token)
