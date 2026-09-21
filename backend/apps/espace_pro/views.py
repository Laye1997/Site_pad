"""Authentification et tableau de bord de l'espace professionnel."""

from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


class ProLoginView(auth_views.LoginView):
    template_name = "espace_pro/login.html"
    redirect_authenticated_user = True


@login_required
def dashboard(request):
    """Tableau de bord minimal réservé aux professionnels authentifiés."""
    return render(request, "espace_pro/dashboard.html")
