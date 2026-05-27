from django.urls import path
from . import views

app_name = "commons"

urlpatterns = [
    path("", views.LandingView.as_view(), name="landing"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("privacy/", views.PrivacyView.as_view(), name="privacy"),
    path("terms/", views.TermsView.as_view(), name="terms"),
    path("contact/", views.ContactView.as_view(), name="contact"),
    path("contact/sent/", views.ContactSuccessView.as_view(), name="contact_success"),
    path("guidelines/", views.GuidelinesView.as_view(), name="guidelines"),
]
