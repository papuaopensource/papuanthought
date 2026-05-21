from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("site-manager/", admin.site.urls),
    path("", include("accounts.urls")),
    path("", include("commons.urls")),
    path("", include("interactions.urls")),
    path("", include("essays.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
