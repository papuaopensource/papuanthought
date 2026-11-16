from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = "commons"

urlpatterns = [
    # No public landing page: the root goes to the feed (or to login).
    path("", RedirectView.as_view(pattern_name="posts:feed"), name="home"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("privacy/", views.PrivacyView.as_view(), name="privacy"),
    path("terms/", views.TermsView.as_view(), name="terms"),
    path("feedback/", views.FeedbackView.as_view(), name="feedback"),
    path("feedback/sent/", views.FeedbackSentView.as_view(), name="feedback_sent"),
    # The contact page became the feedback page; keep old links working.
    path("contact/", RedirectView.as_view(pattern_name="commons:feedback")),
    path("guidelines/", views.GuidelinesView.as_view(), name="guidelines"),
]
