from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_not_required
from django.views.static import serve

urlpatterns = [
    path("site-manager/", admin.site.urls),
    path("", include("accounts.urls"), name="accounts"),
    path("", include("commons.urls"), name="commons"),
    path("", include("interactions.urls"), name="interactions"),
    path("", include("essays.urls"), name="essays"),
]

if settings.DEBUG:
    # Media must load for signed-out readers of public articles too (in production
    # the web server serves /media/ directly, outside Django).
    urlpatterns += static(
        settings.MEDIA_URL,
        view=login_not_required(serve),
        document_root=settings.MEDIA_ROOT,
    )
