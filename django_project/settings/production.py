from decouple import config
from .base import *  # noqa: F401, F403

DEBUG = False

# Security
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# ── Database ──────────────────────────────────────────
# SQLite in WAL mode: readers never block the writer, which is what lets a
# single file serve a live site. Note that db.sqlite3 alone is not a complete
# snapshot — the -wal file holds recent transactions, so a backup has to go
# through `sqlite3 .backup` rather than a plain copy.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        "OPTIONS": {
            "transaction_mode": "IMMEDIATE",
            "timeout": 5,
            "init_command": """PRAGMA journal_mode=WAL;
    PRAGMA synchronous=NORMAL;
    PRAGMA temp_store=MEMORY;
    PRAGMA mmap_size=134217728;
    PRAGMA journal_size_limit=27103364;
    PRAGMA cache_size=2000;""",
        },
    }
}

# ── Email ─────────────────────────────────────────────
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
