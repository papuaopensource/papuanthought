from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import DetailView, TemplateView
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse

from .models import User, Profile, Invitation
from . import services


class LoginView(View):
    template_name = "accounts/login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("essays:feed")
        return render(request, self.template_name)

    def post(self, request):
        credential = request.POST.get("credential", "").strip()
        password = request.POST.get("password", "")
        user = services.authenticate_user(credential, password, request)
        if user:
            login(request, user)
            next_url = request.GET.get("next", reverse("essays:feed"))
            return redirect(next_url)
        # Check if account exists but is pending approval
        pending = (
            User.objects.filter(username=credential, is_active=False).exists()
            or User.objects.filter(email=credential, is_active=False).exists()
        )
        if pending:
            return render(
                request,
                self.template_name,
                {"error": "Your application is pending admin approval."},
            )
        return render(request, self.template_name, {"error": "Invalid credentials."})


class JoinView(View):
    template_name = "accounts/join.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("essays:feed")
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        motivation = request.POST.get("motivation", "").strip()

        errors = {}
        if not username:
            errors["username"] = "Username is required."
        if not email:
            errors["email"] = "Email is required."
        if not password or len(password) < 8:
            errors["password"] = "Password must be at least 8 characters."
        if not motivation:
            errors["motivation"] = "Tell us a bit about yourself."

        if errors:
            return render(
                request,
                self.template_name,
                {
                    "errors": errors,
                    "form_data": {
                        "username": username,
                        "email": email,
                        "motivation": motivation,
                    },
                },
            )

        try:
            services.apply_for_membership(username, email, password, motivation)
            return redirect("accounts:join_pending")
        except ValueError as e:
            return render(
                request,
                self.template_name,
                {
                    "error": str(e),
                    "form_data": {
                        "username": username,
                        "email": email,
                        "motivation": motivation,
                    },
                },
            )


class JoinPendingView(TemplateView):
    template_name = "accounts/join_pending.html"


class InvitationAcceptView(View):
    template_name = "accounts/invitation_accept.html"

    def _get_invitation(self, token):
        return get_object_or_404(Invitation, token=token, used_at__isnull=True)

    def get(self, request, token):
        invitation = self._get_invitation(token)
        return render(request, self.template_name, {"invitation": invitation})

    def post(self, request, token):
        invitation = self._get_invitation(token)
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        errors = {}
        if not username:
            errors["username"] = "Username is required."
        if not password or len(password) < 8:
            errors["password"] = "Password must be at least 8 characters."

        if errors:
            return render(
                request,
                self.template_name,
                {
                    "invitation": invitation,
                    "errors": errors,
                    "form_data": {"username": username},
                },
            )

        try:
            user = services.accept_invitation(str(token), username, password)
            login(request, user, backend="accounts.backends.EmailOrUsernameBackend")
            return redirect("essays:feed")
        except ValueError as e:
            return render(
                request,
                self.template_name,
                {
                    "invitation": invitation,
                    "error": str(e),
                    "form_data": {"username": username},
                },
            )


class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect("essays:feed")


class ProfileView(DetailView):
    model = User
    template_name = "accounts/profile.html"
    slug_field = "username"
    slug_url_kwarg = "username"
    context_object_name = "profile_user"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from essays.models import Essay as EssayModel

        context["essays"] = self.object.essays.filter(
            status=EssayModel.PUBLISHED
        ).order_by("-published_at")
        from interactions.models import Follow, Reaction

        if self.request.user == self.object:
            context["draft_essays"] = self.object.essays.filter(
                status=EssayModel.DRAFT
            ).order_by("-created_at")
            context["bookmarked_essays"] = (
                EssayModel.objects.filter(
                    bookmarks__user=self.object,
                    status=EssayModel.PUBLISHED,
                )
                .select_related("author", "author__profile")
                .order_by("-bookmarks__created_at")
            )
            context["followers_list"] = (
                Follow.objects.filter(following=self.object)
                .select_related("follower", "follower__profile")
                .order_by("-created_at")
            )
        else:
            context["draft_essays"] = None
            context["bookmarked_essays"] = None
            context["followers_list"] = None
        context["is_following"] = False
        if self.request.user.is_authenticated and self.request.user != self.object:
            context["is_following"] = Follow.objects.filter(
                follower=self.request.user, following=self.object
            ).exists()
        context["follower_count"] = self.object.followers.count()
        context["total_likes"] = Reaction.objects.filter(
            essay__author=self.object, reaction_type=Reaction.HEART
        ).count()
        return context


class ProfileEditView(LoginRequiredMixin, View):
    def get(self, request):
        return redirect("accounts:settings_profile")

    def post(self, request):
        return redirect("accounts:settings_profile")


class SettingsProfileView(LoginRequiredMixin, View):
    template_name = "accounts/settings_profile.html"

    def _ctx(self, request, **extra):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        return {"profile": profile, "active_section": "profile", **extra}

    def get(self, request):
        return render(request, self.template_name, self._ctx(request))

    def post(self, request):
        data = {
            "first_name": request.POST.get("first_name", "").strip(),
            "last_name": request.POST.get("last_name", "").strip(),
            "bio": request.POST.get("bio", "").strip(),
            "location": request.POST.get("location", "").strip(),
            "website": request.POST.get("website", "").strip(),
            "twitter": request.POST.get("twitter", "").strip(),
            "instagram": request.POST.get("instagram", "").strip(),
        }
        photo = request.FILES.get("photo")
        services.update_profile(request.user, photo=photo, **data)
        return render(request, self.template_name, self._ctx(request, success="Profile updated."))


class SettingsIndexView(LoginRequiredMixin, View):
    template_name = "accounts/settings_index.html"

    def get(self, request):
        return render(request, self.template_name)


class SettingsPasswordView(LoginRequiredMixin, View):
    template_name = "accounts/settings_password.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        old_pw = request.POST.get("old_password", "")
        new_pw = request.POST.get("new_password", "")
        confirm_pw = request.POST.get("confirm_password", "")
        if new_pw != confirm_pw:
            return render(request, self.template_name, {"error": "Passwords do not match."})
        if len(new_pw) < 8:
            return render(request, self.template_name, {"error": "Password must be at least 8 characters."})
        if not services.change_password(request.user, old_pw, new_pw):
            return render(request, self.template_name, {"error": "Current password is incorrect."})
        update_session_auth_hash(request, request.user)
        return render(request, self.template_name, {"success": "Password updated successfully."})


class SettingsDeleteAccountView(LoginRequiredMixin, View):
    def post(self, request):
        password = request.POST.get("password", "")
        if not request.user.check_password(password):
            return render(request, "accounts/settings_account.html", {
                "active_section": "account",
                "delete_error": "Incorrect password. Account was not deleted.",
            })
        logout(request)
        services.delete_account(request.user)
        return redirect("essays:feed")
