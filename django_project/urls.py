from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("site-manager/", admin.site.urls),
    path("", include("accounts.urls"), name="accounts"),
    path("", include("commons.urls"), name="commons"),
    path("", include("interactions.urls"), name="interactions"),
    path("", include("essays.urls"), name="essays"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
