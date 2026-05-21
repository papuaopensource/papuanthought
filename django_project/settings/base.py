from pathlib import Path
from django.urls import reverse_lazy
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
    "django.contrib.staticfiles",
    # Third-party apps
    "tailwind",
    "theme",
    # Local apps
    "accounts",
    "essays",
    "interactions",
    "commons",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
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

LANGUAGE_CODE = "id-ID"
TIME_ZONE = "Asia/Jayapura"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

TAILWIND_APP_NAME = "theme"

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "essays:feed"
LOGOUT_REDIRECT_URL = "essays:feed"

EMAIL_BACKEND = config(
    "EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = config("EMAIL_HOST", default="localhost")
EMAIL_PORT = config("EMAIL_PORT", default=25, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=False, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="noreply@papuanthought.org")

UNFOLD = {
    "SITE_TITLE": "The Papuan Thoughts Project",
    "SITE_HEADER": "Papuan Thoughts",
    "SITE_DESCRIPTION": "A platform for sharing thoughts and ideas from the Papuan community.",
    "SITE_URL": "/",
    "SITE_SYMBOL": "newspaper",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": False,
    "COLORS": {
        "font": {
            "subtle-light": "115 115 115",
            "subtle-dark": "163 163 163",
            "default-light": "64 64 64",
            "default-dark": "212 212 212",
            "important-light": "10 10 10",
            "important-dark": "250 250 250",
        },
        "primary": {
            "50": "250 250 250",
            "100": "245 245 245",
            "200": "229 229 229",
            "300": "212 212 212",
            "400": "163 163 163",
            "500": "115 115 115",
            "600": "82 82 82",
            "700": "64 64 64",
            "800": "38 38 38",
            "900": "23 23 23",
            "950": "10 10 10",
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
                "title": "Essays",
                "separator": True,
                "items": [
                    {
                        "title": "All Essays",
                        "icon": "article",
                        "link": reverse_lazy("admin:essays_essay_changelist"),
                    },
                    {
                        "title": "Tags",
                        "icon": "tag",
                        "link": reverse_lazy("admin:essays_tag_changelist"),
                    },
                ],
            },
            {
                "title": "Users",
                "separator": True,
                "items": [
                    {
                        "title": "Member Accounts",
                        "icon": "group",
                        "link": reverse_lazy("admin:accounts_user_changelist"),
                    },
                    {
                        "title": "Profiles",
                        "icon": "person",
                        "link": reverse_lazy("admin:accounts_profile_changelist"),
                    },
                    {
                        "title": "Undangan",
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
                        "title": "Reactions",
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
                "title": "Commons",
                "separator": True,
                "items": [
                    {
                        "title": "Contact Messages",
                        "icon": "mail",
                        "link": reverse_lazy("admin:commons_contactmessage_changelist"),
                    },
                ],
            },
        ],
    },
}
