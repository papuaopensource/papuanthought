from django import template
from django.utils import dateformat, timezone
from django.utils.safestring import mark_safe

from posts.text import markdown_to_text, render_markdown_safe

register = template.Library()


@register.filter
def render_markdown(value):
    """Article body: sanitized Markdown, images allowed (own uploads only)."""
    return mark_safe(render_markdown_safe(value, allow_images=True))


@register.filter
def render_note(value):
    """Note body: sanitized Markdown, no images (notes are text-only)."""
    return mark_safe(render_markdown_safe(value, allow_images=False))


@register.filter
def plain_text(value):
    """Markdown source → plain text, for previews of essays without a subtitle."""
    return markdown_to_text(value)


@register.filter
def short_date(value):
    """'Oct 31' for dates this year, 'Oct 31, 2024' otherwise."""
    if not value:
        return ""
    if timezone.is_aware(value):
        value = timezone.localtime(value)
    fmt = "M j" if value.year == timezone.localtime().year else "M j, Y"
    return dateformat.format(value, fmt)
