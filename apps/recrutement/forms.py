"""Formulaire sécurisé de candidature."""

from django import forms
from django.conf import settings


class ApplicationForm(forms.Form):
    name = forms.CharField(label="Nom complet", max_length=120)
    email = forms.EmailField(label="Adresse e-mail")
    message = forms.CharField(label="Message", widget=forms.Textarea, max_length=5000)
    cv = forms.FileField(label="CV", required=True)
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    def clean_website(self):
        value = self.cleaned_data["website"]
        if value:
            raise forms.ValidationError("Votre candidature n'a pas pu être envoyée.")
        return value

    def clean_cv(self):
        document = self.cleaned_data["cv"]
        allowed_types = {
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }
        max_size = getattr(settings, "APPLICATION_MAX_UPLOAD_SIZE", 5 * 1024 * 1024)
        if document.content_type not in allowed_types:
            raise forms.ValidationError("Le CV doit être au format PDF ou DOCX.")
        if document.size > max_size:
            raise forms.ValidationError("Le CV ne doit pas dépasser 5 Mo.")
        return document
