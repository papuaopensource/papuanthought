from django.urls import path
from . import views

app_name = "interactions"

urlpatterns = [
    path("notifications/", views.NotificationListView.as_view(), name="notifications"),
    path("comment/<int:essay_id>/", views.CommentCreateView.as_view(), name="comment"),
    path("comment/<int:comment_id>/edit/", views.CommentEditView.as_view(), name="comment_edit"),
    path("comment/<int:comment_id>/delete/", views.CommentDeleteView.as_view(), name="comment_delete"),
    path("react/<int:essay_id>/", views.ReactionToggleView.as_view(), name="react"),
    path("follow/<str:username>/", views.FollowToggleView.as_view(), name="follow"),
    path("bookmark/<int:essay_id>/", views.BookmarkToggleView.as_view(), name="bookmark"),
    path("comment/<int:comment_id>/like/", views.CommentLikeToggleView.as_view(), name="comment_like"),
]
