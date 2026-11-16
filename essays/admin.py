from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import Article, ArticleImage, Tag


class ArticleImageInline(TabularInline):
    """Images used in the article body, shown as an "Images" tab on the article."""

    model = ArticleImage
    tab = True
    verbose_name = "Image"
    verbose_name_plural = "Images"
    extra = 0
    can_delete = False
    fields = ("image", "uploader", "created_at")  # unfold renders a preview for the image
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False  # images come from the article editor


@admin.register(Article)
class ArticleAdmin(ModelAdmin):
    list_display = ("title_display", "kind", "author", "status", "is_public", "is_featured", "published_at", "created_at")
    list_filter = ("kind", "status", "is_public", "is_featured")
    search_fields = ("title", "author__username", "content")
    filter_horizontal = ("tags",)
    date_hierarchy = "created_at"
    raw_id_fields = ("author",)
    inlines = [ArticleImageInline]

    @admin.display(description="Title", ordering="title")
    def title_display(self, obj):
        return obj.display_title


@admin.register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
