#!/usr/bin/env bash
# Déploiement de recette du site PAD sur une IP publique, en HTTP.
# Usage (depuis le dossier du projet, à côté de docker-compose.yml) :
#     bash deploy/deploy.sh 102.203.220.55 6060
#
# Ce script : écrit/complète le fichier .env, reconstruit les images, applique les migrations,
# règle le site Wagtail sur l'IP et charge le contenu de départ. Il est relançable sans risque.
# ATTENTION : HTTP seul = recette provisoire. Pas de comptes réels avant d'avoir un certificat.
set -euo pipefail

IP="${1:?Indiquez adresse IP publique, ex. 102.203.220.55}"
PORT="${2:-6060}"
ORIGIN="http://${IP}:${PORT}"

cd "$(dirname "$0")/.."

# 1. Fichier .env : on garde les valeurs existantes, on ajoute ou remplace celles de la recette.
touch .env
set_env() {
  local key="$1" value="$2"
  if grep -q "^${key}=" .env; then
    sed -i "s|^${key}=.*|${key}=${value}|" .env
  else
    echo "${key}=${value}" >> .env
  fi
}
if ! grep -q "^DJANGO_SECRET_KEY=" .env; then
  set_env DJANGO_SECRET_KEY "$(python3 -c 'import secrets; print(secrets.token_urlsafe(60))')"
fi
set_env DJANGO_ALLOWED_HOSTS "${IP},localhost,127.0.0.1"
set_env DJANGO_CSRF_TRUSTED_ORIGINS "${ORIGIN}"
set_env DJANGO_HTTPS "false"
set_env WAGTAILADMIN_BASE_URL "${ORIGIN}"
set_env PUBLIC_PORT "${PORT}"
echo ">> .env prêt"

# 2. Images et services
docker compose up -d --build
echo ">> attente du démarrage de l'application..."
for _ in $(seq 1 30); do
  if docker compose exec -T web python manage.py check >/dev/null 2>&1; then break; fi
  sleep 3
done

# 3. Base de données et site Wagtail (racine = page d'accueil, adresse = IP publique)
docker compose exec -T web python manage.py migrate --noinput
docker compose exec -T web python manage.py setup_site --host "${IP}" --port "${PORT}"

# 4. Contenu de départ (sans écraser ce qui existe)
for cmd in seed_site_structure seed_legal_pages seed_home_sections seed_partners \
           seed_certifications seed_passation_article seed_old_articles seed_ndayane_article; do
  echo ">> ${cmd}"
  docker compose exec -T web python manage.py "${cmd}" || echo "   (ignoré : ${cmd} a échoué)"
done

# 5. Contrôle final
echo ">> contrôle"
CODE=$(curl -s -o /dev/null -w '%{http_code}' "http://localhost:${PORT}/fr/" -H "Host: ${IP}:${PORT}" || true)
echo "GET /fr/ -> HTTP ${CODE} (attendu : 200)"
echo "Site : ${ORIGIN}/fr/    Administration : ${ORIGIN}/admin/"
echo "Créer un administrateur si besoin : docker compose exec web python manage.py createsuperuser"
