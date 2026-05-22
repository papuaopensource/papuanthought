import re
import markdown
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

# Python-Markdown parses `> text\n---` as a Setext h2 instead of blockquote + hr.
# Insert a blank line before any --- / === that immediately follows a blockquote line.
_SETEXT_AFTER_QUOTE = re.compile(r'^(>.+)\n([-=]{3,}\s*)$', re.MULTILINE)


@register.filter
def render_markdown(value):
    if not value:
        return mark_safe("")
    content = _SETEXT_AFTER_QUOTE.sub(r'\1\n\n\2', value)
    md = markdown.Markdown(extensions=["extra", "nl2br", "sane_lists"])
    return mark_safe(md.convert(content))
