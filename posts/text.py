import html
import re

import markdown
from django.utils.html import strip_tags

# Python-Markdown parses `> text\n---` as a Setext h2 instead of blockquote + hr.
# Insert a blank line before any --- / === that immediately follows a blockquote line.
SETEXT_AFTER_QUOTE = re.compile(r'^(>.+)\n([-=]{3,}\s*)$', re.MULTILINE)


def markdown_to_text(value: str) -> str:
    """Markdown source -> single-line plain text (for previews and titles)."""
    if not value:
        return ""
    rendered = markdown.markdown(SETEXT_AFTER_QUOTE.sub(r'\1\n\n\2', value), extensions=["extra"])
    return " ".join(html.unescape(strip_tags(rendered)).split())


# ── Rendering user-written Markdown safely ──────────────────────────────────
# Python-Markdown passes raw HTML through, so everything it produces is cleaned
# with nh3 against an allowlist before it reaches a template.

_BASE_TAGS = {
    "p", "br", "hr", "h1", "h2", "h3", "h4", "h5", "h6",
    "strong", "b", "em", "i", "del", "s", "sup", "sub", "abbr",
    "blockquote", "ul", "ol", "li", "dl", "dt", "dd",
    "a", "code", "pre", "table", "thead", "tbody", "tr", "th", "td", "div",
}
_BASE_ATTRIBUTES = {
    "a": {"href", "title"},
    "abbr": {"title"},
    "li": {"id"},   # footnotes
    "sup": {"id"},  # footnote references
}


_IMG_WITHOUT_SRC = re.compile(r"<img(?![^>]*\ssrc=)[^>]*>")


def _media_prefix() -> str:
    """URL prefix that images in articles must start with (our own media storage)."""
    from django.conf import settings

    url = settings.MEDIA_URL or "/media/"
    if not url.startswith(("http://", "https://", "/")):
        url = "/" + url
    return url


def _attribute_filter(tag, attribute, value):
    if attribute == "id":
        return value if value.startswith("fn") else None  # only footnote anchors
    if tag == "img" and attribute == "src":
        prefix = _media_prefix()
        if value.startswith(prefix) and not value.startswith("//"):
            return value
        return None  # images must come from our own uploads
    return value


def render_markdown_safe(value: str, allow_images: bool) -> str:
    """Markdown -> sanitized HTML. Images (own uploads only) when `allow_images`."""
    import nh3

    if not value:
        return ""
    md = markdown.Markdown(extensions=["extra", "nl2br", "sane_lists"])
    html = md.convert(SETEXT_AFTER_QUOTE.sub(r'\1\n\n\2', value))
    tags = set(_BASE_TAGS)
    attributes = {tag: set(attrs) for tag, attrs in _BASE_ATTRIBUTES.items()}
    if allow_images:
        tags.add("img")
        attributes["img"] = {"src", "alt", "title"}
    cleaned = nh3.clean(
        html,
        tags=tags,
        attributes=attributes,
        attribute_filter=_attribute_filter,
        url_schemes={"http", "https", "mailto"},
        link_rel="noopener noreferrer nofollow",
        set_tag_attribute_values={"img": {"loading": "lazy", "decoding": "async"}} if allow_images else None,
    )
    # An <img> whose src was rejected would render as a broken image; drop it entirely.
    return _IMG_WITHOUT_SRC.sub("", cleaned)
