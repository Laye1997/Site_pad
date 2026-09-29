"""Crée un compte administrateur au démarrage, pour les hébergeurs sans terminal.

Lit DJANGO_SUPERUSER_USERNAME / _EMAIL / _PASSWORD (mêmes noms que la commande standard
`createsuperuser --noinput` de Django). Sans ces variables, ne fait rien. Idempotent : si le
compte existe déjà, ne le modifie pas — pour changer le mot de passe, utilisez l'admin Wagtail.
Le mot de passe n'apparaît jamais dans la sortie de la commande.
"""

import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Crée un compte administrateur depuis DJANGO_SUPERUSER_USERNAME/_EMAIL/_PASSWORD."

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "").strip()
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "").strip()
        if not username or not password:
            self.stdout.write(
                "DJANGO_SUPERUSER_USERNAME/_PASSWORD non définies : aucun compte créé."
            )
            return
        user_model = get_user_model()
        if user_model.objects.filter(username=username).exists():
            self.stdout.write(f"Compte administrateur déjà présent : {username}.")
            return
        user_model.objects.create_superuser(username, email, password)
        self.stdout.write(f"Compte administrateur créé : {username}.")
