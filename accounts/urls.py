from django.contrib.auth.decorators import login_not_required
from django.urls import path
from . import views

app_name = "accounts"

# Members-only site: only sign-in and invitation acceptance are public (there is
# no open sign-up). LoginRequiredMiddleware protects everything else.
urlpatterns = [
    path("login/", login_not_required(views.LoginView.as_view()), name="login"),
    path("join/invite/<uuid:token>/", login_not_required(views.InvitationAcceptView.as_view()), name="invitation_accept"),
    path("logout/", login_not_required(views.LogoutView.as_view()), name="logout"),
    path("profile/edit/", views.ProfileEditView.as_view(), name="profile_edit"),
    path("profile/<str:username>/", views.ProfileView.as_view(), name="profile"),
    path("settings/", views.SettingsIndexView.as_view(), name="settings"),
    path("settings/profile/", views.SettingsProfileView.as_view(), name="settings_profile"),
    path("settings/password/", views.SettingsPasswordView.as_view(), name="settings_password"),
    path("settings/delete/", views.SettingsDeleteAccountView.as_view(), name="settings_delete"),
]
