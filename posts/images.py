"""
Image uploads for articles (cover images and images inside the article body).

Every upload is decoded and re-encoded with Pillow, which:
  - rejects files that are not real images, or are too big to be reasonable;
  - applies the camera's EXIF rotation, then drops all metadata (EXIF, GPS location);
  - downsizes to a sensible maximum and stores a compact WebP.

Files are saved through Django's storage API, so moving from local `mediafiles/`
to object storage (e.g. Cloudflare R2 via django-storages) is configuration only.
"""

import io
import uuid

from django.core.files.base import ContentFile
from PIL import Image, ImageOps, UnidentifiedImageError

MAX_UPLOAD_BYTES = 5 * 1024 * 1024
MAX_SOURCE_PIXELS = 40_000_000  # ~ 8000 x 5000
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP", "GIF"}
ACCEPT_ATTR = "image/jpeg,image/png,image/webp,image/gif"

BODY_MAX_SIZE = (1600, 3200)
COVER_MAX_SIZE = (1600, 1600)


class ImageRejected(ValueError):
    """Raised with a user-facing message when an upload can't be used."""


def process_upload(uploaded, max_size=BODY_MAX_SIZE) -> ContentFile:
    """Validate an uploaded file and return a clean WebP ready to save."""
    if uploaded.size > MAX_UPLOAD_BYTES:
        raise ImageRejected("Images can be up to 5 MB.")
    try:
        with Image.open(uploaded) as probe:
            source_format = probe.format
            width, height = probe.size
            probe.verify()
        if source_format not in ALLOWED_FORMATS:
            raise ImageRejected("Use a JPEG, PNG, WebP or GIF image.")
        if width * height > MAX_SOURCE_PIXELS:
            raise ImageRejected("That image is too large. Try a smaller one.")
        uploaded.seek(0)
        image = Image.open(uploaded)
        image.load()
    except ImageRejected:
        raise
    except (UnidentifiedImageError, Image.DecompressionBombError, OSError, SyntaxError, ValueError):
        raise ImageRejected("That file is not a valid image.")

    image = ImageOps.exif_transpose(image)  # keep the photo upright before metadata is dropped
    has_alpha = image.mode in ("RGBA", "LA") or (
        image.mode == "P" and "transparency" in image.info
    )
    image = image.convert("RGBA" if has_alpha else "RGB")
    image.thumbnail(max_size, Image.Resampling.LANCZOS)

    buffer = io.BytesIO()
    image.save(buffer, format="WEBP", quality=82, method=4)  # no exif= → metadata is not written
    return ContentFile(buffer.getvalue(), name=f"{uuid.uuid4().hex}.webp")
