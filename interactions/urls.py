from django.urls import path
from . import views

app_name = "interactions"

urlpatterns = [
    path("notifications/", views.NotificationListView.as_view(), name="notifications"),
    path("comment/<int:article_id>/", views.CommentCreateView.as_view(), name="comment"),
    path("comment/<int:comment_id>/edit/", views.CommentEditView.as_view(), name="comment_edit"),
    path("comment/<int:comment_id>/delete/", views.CommentDeleteView.as_view(), name="comment_delete"),
    path("react/<int:article_id>/", views.ReactionToggleView.as_view(), name="react"),
    path("follow/<str:username>/", views.FollowToggleView.as_view(), name="follow"),
    path("comment/<int:comment_id>/like/", views.CommentLikeToggleView.as_view(), name="comment_like"),
    path("report/article/<int:article_id>/", views.ReportArticleView.as_view(), name="report_article"),
    path("report/comment/<int:comment_id>/", views.ReportCommentView.as_view(), name="report_comment"),
    path("report/user/<str:username>/", views.ReportUserView.as_view(), name="report_user"),
]
