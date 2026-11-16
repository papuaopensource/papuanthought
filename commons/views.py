from django.views import View
from django.views.generic import TemplateView
from django.shortcuts import render, redirect

from .models import Feedback


class AboutView(TemplateView):
    template_name = "commons/about.html"


class PrivacyView(TemplateView):
    template_name = "commons/privacy.html"


class TermsView(TemplateView):
    template_name = "commons/terms.html"


class GuidelinesView(TemplateView):
    template_name = "commons/guidelines.html"


class FeedbackView(View):
    """Members send ideas, bug reports and questions to the team."""

    template_name = "commons/feedback.html"

    def get(self, request):
        return render(request, self.template_name, {"categories": Feedback.CATEGORY_CHOICES})

    def post(self, request):
        category = request.POST.get("category", "")
        message = request.POST.get("message", "").strip()
        error = None
        if category not in dict(Feedback.CATEGORY_CHOICES):
            error = "Choose what your feedback is about."
        elif not message:
            error = "Write your feedback first."
        if error:
            return render(request, self.template_name, {
                "categories": Feedback.CATEGORY_CHOICES,
                "error": error,
                "category": category,
                "message": message,
            })

        # The site is members-only, so the sender is always the signed-in user.
        user = request.user
        Feedback.objects.create(
            user=user,
            category=category,
            name=(user.get_full_name() or user.username)[:150],
            email=user.email,
            message=message,
        )
        return redirect("commons:feedback_sent")


class FeedbackSentView(TemplateView):
    template_name = "commons/feedback_sent.html"
