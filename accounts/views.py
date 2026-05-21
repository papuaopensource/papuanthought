from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import DetailView
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse

from .models import User, Profile
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
            next_url = request.GET.get("next", "essays:feed")
            return redirect(next_url)
        return render(request, self.template_name, {"error": "Invalid credentials."})


class RegisterView(View):
    template_name = "accounts/register.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("essays:feed")
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        try:
            user = services.register_user(username, email, password)
            login(request, user, backend="accounts.backends.EmailOrUsernameBackend")
            return redirect("essays:feed")
        except ValueError as e:
            return render(request, self.template_name, {"error": str(e)})


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
        context["essays"] = (
            self.object.essays.filter(status=EssayModel.PUBLISHED)
            .order_by("-published_at")
        )
        if self.request.user == self.object:
            context["bookmarked_essays"] = (
                EssayModel.objects.filter(
                    bookmarks__user=self.object,
                    status=EssayModel.PUBLISHED,
                )
                .select_related("author", "author__profile")
                .order_by("-bookmarks__created_at")
            )
        else:
            context["bookmarked_essays"] = None
        context["is_following"] = False
        if self.request.user.is_authenticated and self.request.user != self.object:
            from interactions.models import Follow
            context["is_following"] = Follow.objects.filter(
                follower=self.request.user, following=self.object
            ).exists()
        return context


class ProfileEditView(LoginRequiredMixin, View):
    template_name = "accounts/profile_edit.html"

    def get(self, request):
        return render(request, self.template_name, {"profile": request.user.profile})

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
        return redirect("accounts:profile", username=request.user.username)
