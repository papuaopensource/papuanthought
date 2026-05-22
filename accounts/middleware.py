from django.shortcuts import redirect
from django.urls import reverse


class ProfileCompletionMiddleware:
    """
    Redirect authenticated non-staff users to the profile settings page
    until they have set their first name, last name, and bio.
    """

    ALLOWED_PATHS = None

    def __init__(self, get_response):
        self.get_response = get_response

    def _get_allowed_paths(self):
        if self.ALLOWED_PATHS is None:
            ProfileCompletionMiddleware.ALLOWED_PATHS = {
                reverse("accounts:settings_profile"),
                reverse("accounts:logout"),
                reverse("accounts:login"),
            }
        return self.ALLOWED_PATHS

    @staticmethod
    def _profile_complete(user):
        if not (user.first_name and user.last_name):
            return False
        try:
            return bool(user.profile.bio) and bool(user.profile.location)
        except Exception:
            return False

    def __call__(self, request):
        if (
            request.user.is_authenticated
            and not request.user.is_staff
            and not request.user.is_superuser
            and not self._profile_complete(request.user)
        ):
            allowed = self._get_allowed_paths()
            if (
                request.path not in allowed
                and not request.path.startswith("/admin/")
                and not request.path.startswith("/media/")
                and not request.path.startswith("/static/")
            ):
                return redirect(reverse("accounts:settings_profile"))

        return self.get_response(request)
