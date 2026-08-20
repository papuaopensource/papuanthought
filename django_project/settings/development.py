from .base import BASE_DIR
from .base import *  # noqa: F401, F403

DEBUG = True

# ── Database ──────────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# ── Email ─────────────────────────────────────────────
# Printed to the console instead of sent, so registration and password-reset
# flows can be walked through without an SMTP account.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
