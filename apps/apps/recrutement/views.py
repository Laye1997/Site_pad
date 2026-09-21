"""Candidature en ligne."""

from django.conf import settings
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render

from apps.recrutement.forms import ApplicationForm


def apply(request):
    if request.method == "POST":
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.cleaned_data["message"]
            email = EmailMessage(
                subject=f"Candidature de {form.cleaned_data['name']}",
                body=(
                    f"Nom : {form.cleaned_data['name']}\n"
                    f"E-mail : {form.cleaned_data['email']}\n\n{message}"
                ),
                to=[settings.RECRUITMENT_EMAIL],
                reply_to=[form.cleaned_data["email"]],
            )
            email.attach(
                form.cleaned_data["cv"].name,
                form.cleaned_data["cv"].read(),
                form.cleaned_data["cv"].content_type,
            )
            email.send()
            return redirect("recrutement:confirmation")
    else:
        form = ApplicationForm()
    return render(request, "recrutement/apply.html", {"form": form})


def confirmation(request):
    return render(request, "recrutement/confirmation.html")
