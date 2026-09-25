#!/bin/sh
# Préparation optionnelle au démarrage du conteneur, pour les hébergeurs sans terminal.
# Le serveur web démarre IMMÉDIATEMENT (le port 8000 répond en quelques secondes : les contrôles
# de santé des hébergeurs échouent si le port reste fermé pendant les migrations). La préparation
# de la base se fait en arrière-plan ; /healthz/ répond sans base, le site suit une fois prêt.
#   RUN_MIGRATIONS=true  : crée/met à jour les tables et règle le site Wagtail
#   SEED_ON_START=true   : charge ensuite le contenu de départ (idempotent)
#   SITE_HOST / SITE_PORT : adresse publique enregistrée dans Wagtail (défaut : localhost:80)
# La liste ci-dessous reprend celle de deploy/deploy.sh : la garder identique.
set -e

if [ "${RUN_MIGRATIONS:-false}" = "true" ] || [ "${SEED_ON_START:-false}" = "true" ]; then
  (
    if [ "${RUN_MIGRATIONS:-false}" = "true" ]; then
      python manage.py migrate --noinput
      python manage.py setup_site --host "${SITE_HOST:-localhost}" --port "${SITE_PORT:-80}"
    fi
    if [ "${SEED_ON_START:-false}" = "true" ]; then
      for cmd in seed_site_structure seed_legal_pages seed_home_sections update_home_services \
                 seed_partners seed_certifications update_notes_images update_rubric_photos \
                 seed_fondation seed_croisieres seed_infos_pratiques seed_trafic_passagers \
                 seed_marchandises seed_agrements update_service_nautique seed_passation_article \
                 seed_old_articles seed_ndayane_article seed_organigramme seed_espace_pro; do
        echo ">> ${cmd}"
        python manage.py "${cmd}" || echo "   (ignoré : ${cmd} a échoué)"
      done
    fi
    echo ">> préparation terminée"
  ) &
fi

exec "$@"
