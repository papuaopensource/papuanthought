from pathlib import Path
from django.templatetags.static import static
from django.urls import reverse_lazy

from interactions.badges import OpenReportsBadge
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config(
    "SECRET_KEY", default="django-insecure-dev-key-change-in-production"
)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())

INSTALLED_APPS = [
    # django-unfold must come before django.contrib.admin
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",
    # Django built-in apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sites",
    "whitenoise.runserver_nostatic",  # 3rd-party
    "django.contrib.staticfiles",
    # Third-party apps
    "tailwind",
    "theme",
    # Local apps
    "accounts",
    "posts",
    "interactions",
    "commons",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # 3rd-party
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # The whole site is members-only: every view requires login unless it is
    # wrapped in login_not_required() (see accounts/urls.py).
    "django.contrib.auth.middleware.LoginRequiredMiddleware",
    "accounts.middleware.ProfileCompletionMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "django_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "interactions.context_processors.unread_notifications",
                "accounts.context_processors.sidebar_context",
            ],
        },
    },
]

WSGI_APPLICATION = "django_project.wsgi.application"

AUTH_USER_MODEL = "accounts.User"

AUTHENTICATION_BACKENDS = [
    "accounts.backends.EmailOrUsernameBackend",
    "django.contrib.auth.backends.ModelBackend",
]

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-US"
TIME_ZONE = "Asia/Jayapura"
USE_I18N = True
USE_TZ = True

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "mediafiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SITE_ID = 1

TAILWIND_APP_NAME = "theme"

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "posts:feed"
LOGOUT_REDIRECT_URL = "accounts:login"

# SMTP connection details are shared by development and production. Tests use
# Django's in-memory backend automatically, so they never contact this server.
# ── Email ─────────────────────────────────────────────
EMAIL_HOST = config("EMAIL_HOST", default="localhost")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config(
    "DEFAULT_FROM_EMAIL",
    default=EMAIL_HOST_USER or "noreply@papuanthought.com",
)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_USE_SSL = False
EMAIL_TIMEOUT = 15

UNFOLD = {
    "SITE_TITLE": "Papuan Thought",
    "SITE_HEADER": "Papuan Thought",
    "SITE_DESCRIPTION": "A platform for sharing thoughts and ideas from the Papuan community.",
    "SITE_URL": "/",
    "SITE_ICON": {
        "light": lambda request: static("logo/papuan-thought-inverse-transparent.png"),
        "dark": lambda request: static("logo/papuan-thought-primary-transparent.png"),
    },
    "SITE_FAVICONS": [
        {"rel": "icon", "type": "image/svg+xml", "href": lambda request: static("favicon/favicon.svg")},
        {"rel": "icon", "sizes": "96x96", "type": "image/png", "href": lambda request: static("favicon/favicon-96x96.png")},
    ],
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": False,
    "COLORS": {
        # Neutral greys matching the site's dark palette (#161718 page, #1b1c1d cards).
        "base": {
            "50": "250 250 250",
            "100": "245 245 245",
            "200": "230 230 230",
            "300": "212 212 212",
            "400": "163 163 163",
            "500": "133 133 133",
            "600": "87 87 88",
            "700": "54 55 55",
            "800": "49 50 51",
            "900": "27 28 29",
            "950": "22 23 24",
        },
        # Clay / terracotta, the site accent (#c96442 dark / #b4552f light).
        "primary": {
            "50": "251 241 237",
            "100": "246 225 216",
            "200": "239 197 180",
            "300": "229 160 133",
            "400": "217 119 87",
            "500": "201 100 66",
            "600": "180 85 47",
            "700": "154 69 39",
            "800": "124 56 33",
            "900": "99 46 29",
            "950": "54 24 14",
        },
        "font": {
            "subtle-light": "115 115 115",
            "subtle-dark": "133 133 133",
            "default-light": "54 55 55",
            "default-dark": "212 212 212",
            "important-light": "22 23 24",
            "important-dark": "238 238 238",
        },
    },
    "SIDEBAR": {
        "show_search": False,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Dashboard",
                "separator": False,
                "items": [
                    {
                        "title": "Overview",
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                    },
                ],
            },
            {
                "title": "Posts",
                "separator": True,
                "items": [
                    {
                        "title": "Articles",
                        "icon": "article",
                        "link": reverse_lazy("admin:posts_article_changelist"),
                    },
                    {
                        "title": "Tags",
                        "icon": "tag",
                        "link": reverse_lazy("admin:posts_tag_changelist"),
                    },
                ],
            },
            {
                "title": "Users",
                "separator": True,
                "items": [
                    {
                        "title": "Accounts",
                        "icon": "group",
                        "link": reverse_lazy("admin:accounts_user_changelist"),
                    },
                    {
                        "title": "Invitations",
                        "icon": "mail",
                        "link": reverse_lazy("admin:accounts_invitation_changelist"),
                    },
                ],
            },
            {
                "title": "Interactions",
                "separator": True,
                "items": [
                    {
                        "title": "Comments",
                        "icon": "comment",
                        "link": reverse_lazy("admin:interactions_comment_changelist"),
                    },
                    {
                        "title": "Likes",
                        "icon": "favorite",
                        "link": reverse_lazy("admin:interactions_reaction_changelist"),
                    },
                    {
                        "title": "Notifications",
                        "icon": "notifications",
                        "link": reverse_lazy(
                            "admin:interactions_notification_changelist"
                        ),
                    },
                ],
            },
            {
                "title": "Moderation",
                "separator": True,
                "items": [
                    {
                        "title": "Reports",
                        "icon": "flag",
                        "link": reverse_lazy("admin:interactions_report_changelist"),
                        "badge": OpenReportsBadge(),  # hidden when there are no open reports
                    },
                ],
            },
            {
                "title": "Commons",
                "separator": True,
                "items": [
                    {
                        "title": "Feedback",
                        "icon": "feedback",
                        "link": reverse_lazy("admin:commons_feedback_changelist"),
                    },
                ],
            },
        ],
    },
}
