from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import DetailView
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from .models import User, Profile, Invitation
from . import services


class LoginView(View):
    template_name = "accounts/login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("posts:feed")
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        context = {"email": email}
        user = services.authenticate_by_email(email, password, request)
        if user:
            login(request, user)
            next_url = request.GET.get("next", "")
            if not url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                next_url = reverse("posts:feed")
            return redirect(next_url)
        if User.objects.filter(email__iexact=email, is_active=False).exists():
            context["error"] = "This account is not active. Please contact the admin."
        else:
            context["error"] = "Incorrect email or password."
        return render(request, self.template_name, context)


class InvitationAcceptView(View):
    template_name = "accounts/invitation_accept.html"

    def _get_invitation(self, token):
        return get_object_or_404(Invitation, token=token, used_at__isnull=True)

    def get(self, request, token):
        invitation = self._get_invitation(token)
        return render(request, self.template_name, {"invitation": invitation})

    def post(self, request, token):
        invitation = self._get_invitation(token)
        email = request.POST.get("email", "").strip()
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        errors = {}
        if not email:
            errors["email"] = "Email is required."
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
                    "form_data": {"email": email, "username": username},
                },
            )

        try:
            user = services.accept_invitation(str(token), email, username, password)
            login(request, user, backend="accounts.backends.EmailOrUsernameBackend")
            return redirect("posts:feed")
        except ValueError as e:
            return render(
                request,
                self.template_name,
                {
                    "invitation": invitation,
                    "error": str(e),
                    "form_data": {"email": email, "username": username},
                },
            )


class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect("accounts:login")


class ProfileView(DetailView):
    model = User
    template_name = "accounts/profile.html"
    slug_field = "username"
    slug_url_kwarg = "username"
    context_object_name = "profile_user"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from posts.models import Article as ArticleModel
        from posts.services import get_liked_by, with_engagement
        from interactions.services import get_hearted_ids

        published = list(
            with_engagement(
                self.object.articles.filter(status=ArticleModel.PUBLISHED)
                .select_related("author", "author__profile")
                .prefetch_related("tags")
                .order_by("-published_at")
            )
        )
        # Articles and notes together, newest first (the profile's Activity tab).
        context["posts"] = published
        from interactions.models import Follow, Reaction

        if self.request.user == self.object:
            context["draft_essays"] = self.object.articles.filter(
                status=ArticleModel.DRAFT
            ).order_by("-created_at")
            context["followers_list"] = (
                Follow.objects.filter(following=self.object)
                .select_related("follower", "follower__profile")
                .order_by("-created_at")
            )
        else:
            context["draft_essays"] = None
            context["followers_list"] = None
        context["is_following"] = False
        if self.request.user.is_authenticated and self.request.user != self.object:
            context["is_following"] = Follow.objects.filter(
                follower=self.request.user, following=self.object
            ).exists()
        # Essays this member liked; visible on their profile to every member.
        context["liked_essays"] = list(get_liked_by(self.object))
        shown_ids = {post.pk for post in published} | {
            essay.pk for essay in context["liked_essays"]
        }
        context["hearted_ids"] = get_hearted_ids(self.request.user, shown_ids)
        context["follower_count"] = self.object.followers.count()
        context["total_likes"] = Reaction.objects.filter(
            article__author=self.object, reaction_type=Reaction.HEART
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
        return redirect("accounts:login")
