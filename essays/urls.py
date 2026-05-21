from django.urls import path
from . import views

app_name = "essays"

urlpatterns = [
    path("", views.EssayFeedView.as_view(), name="feed"),
    path("write/", views.EssayWriteView.as_view(), name="write"),
    path("tag/<slug:slug>/", views.TagDetailView.as_view(), name="tag"),
    path("<str:username>/<slug:slug>/edit/", views.EssayEditView.as_view(), name="edit"),
    path("<str:username>/<slug:slug>/delete/", views.EssayDeleteView.as_view(), name="delete"),
    path("<str:username>/<slug:slug>/", views.EssayDetailView.as_view(), name="detail"),
]
