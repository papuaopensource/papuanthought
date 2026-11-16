from django.contrib.auth.decorators import login_not_required
from django.urls import path
from . import views

app_name = "essays"

urlpatterns = [
    path("feed/", views.EssayFeedView.as_view(), name="feed"),
    path("write/", views.EssayWriteView.as_view(), name="write"),
    path("notes/new/", views.NoteCreateView.as_view(), name="note_new"),
    path("images/upload/", views.ImageUploadView.as_view(), name="image_upload"),
    path("tag/<slug:slug>/", views.TagDetailView.as_view(), name="tag"),
    path("<str:username>/<slug:slug>/edit/", views.EssayEditView.as_view(), name="edit"),
    path("<str:username>/<slug:slug>/delete/", views.EssayDeleteView.as_view(), name="delete"),
    path("<str:username>/<slug:slug>/visibility/", views.ArticleVisibilityView.as_view(), name="visibility"),
    # Public: the view itself lets signed-out visitors read public articles only.
    path("<str:username>/<slug:slug>/", login_not_required(views.EssayDetailView.as_view()), name="detail"),
]
