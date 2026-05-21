from django.views import View
from django.views.generic import TemplateView
from django.shortcuts import render, redirect

from .models import ContactMessage


class AboutView(TemplateView):
    template_name = "commons/about.html"


class PrivacyView(TemplateView):
    template_name = "commons/privacy.html"


class TermsView(TemplateView):
    template_name = "commons/terms.html"


class GuidelinesView(TemplateView):
    template_name = "commons/guidelines.html"


class ContactView(View):
    template_name = "commons/contact.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        message = request.POST.get("message", "").strip()

        errors = {}
        if not name:
            errors["name"] = "Name is required."
        if not email:
            errors["email"] = "Email is required."
        if not message:
            errors["message"] = "Message is required."

        if errors:
            return render(request, self.template_name, {
                "errors": errors,
                "form_data": {"name": name, "email": email, "message": message},
            })

        ContactMessage.objects.create(name=name, email=email, message=message)
        return redirect("commons:contact_success")


class ContactSuccessView(TemplateView):
    template_name = "commons/contact_success.html"
