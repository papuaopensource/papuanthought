import uuid

from django.conf import settings
from django.db import models
from django.utils.text import Truncator, slugify

from .text import markdown_to_text


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, max_length=60)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Article(models.Model):
    """A post: a long-form article (title, subtitle, tags) or a short untitled note."""

    ARTICLE = "article"
    NOTE = "note"
    KIND_CHOICES = [
        (ARTICLE, "Article"),
        (NOTE, "Note"),
    ]
    NOTE_MAX_LENGTH = 3000

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    STATUS_CHOICES = [
        (DRAFT, "Draft"),
        (PUBLISHED, "Published"),
        (ARCHIVED, "Archived"),
    ]

    kind = models.CharField(
        max_length=10, choices=KIND_CHOICES, default=ARTICLE, db_index=True
    )
    title = models.CharField(max_length=255, blank=True, help_text="Empty for notes.")
    slug = models.SlugField(unique=True, max_length=255)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="articles",
    )
    content = models.TextField()
    excerpt = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to="essays/covers/", blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=DRAFT)
    tags = models.ManyToManyField(Tag, blank=True, related_name="articles")
    is_featured = models.BooleanField(default=False)
    is_public = models.BooleanField(
        default=False,
        help_text="Readable by anyone with the link, without signing in (articles only).",
    )
    is_edited = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    read_time = models.PositiveSmallIntegerField(
        default=0, help_text="Estimated read time in minutes."
    )
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]
        verbose_name = "article"
        verbose_name_plural = "articles"

    def __str__(self):
        return self.display_title

    @property
    def is_note(self) -> bool:
        return self.kind == self.NOTE

    @property
    def is_publicly_readable(self) -> bool:
        """Can a visitor who is not signed in read this? Only published, public articles."""
        return self.is_public and self.kind == self.ARTICLE and self.status == self.PUBLISHED

    @property
    def display_title(self) -> str:
        """The title for articles; the opening words for (untitled) notes."""
        if self.title:
            return self.title
        return Truncator(markdown_to_text(self.content)).chars(80) or "Note"

    def save(self, *args, **kwargs):
        if not self.slug:
            # Notes have no title, so they get a short random slug.
            self.slug = slugify(self.title) if self.title else f"note-{uuid.uuid4().hex[:10]}"
        if not self.read_time and self.content:
            self.read_time = max(1, round(len(self.content.split()) / 200))
        super().save(*args, **kwargs)


class ArticleImage(models.Model):
    """An image uploaded from the article editor, kept for moderation and cleanup.

    `article` is set once the image is referenced by a saved article (see
    services.link_body_images); it stays empty for uploads never used.
    """

    uploader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="article_images",
    )
    article = models.ForeignKey(
        Article,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="images",
    )
    image = models.ImageField(upload_to="essays/images/%Y/%m/")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.image.name
