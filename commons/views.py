from django.views.generic import TemplateView


class AboutView(TemplateView):
    template_name = "commons/about.html"


class PrivacyView(TemplateView):
    template_name = "commons/privacy.html"


class TermsView(TemplateView):
    template_name = "commons/terms.html"


class ContactView(TemplateView):
    template_name = "commons/contact.html"


class GuidelinesView(TemplateView):
    template_name = "commons/guidelines.html"
