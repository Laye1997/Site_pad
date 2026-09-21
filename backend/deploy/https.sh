#!/usr/bin/env bash
# Active HTTPS (Let's Encrypt) pour un domaine. À lancer APRÈS que :
#   - le DNS  <domaine> -> IP du serveur existe ;
#   - les ports 80 et 443 sont ouverts chez l'hébergeur.
# Usage : bash backend/deploy/https.sh refonte.portdakar.sn admin@exemple.sn
set -euo pipefail
DOMAIN="${1:?Indiquez le domaine, ex. refonte.portdakar.sn}"
EMAIL="${2:?Indiquez un e-mail (alertes d'expiration Let's Encrypt)}"
cd "$(dirname "$0")/../.."

echo ">> contrôle DNS"
RESOLVED=$(getent hosts "$DOMAIN" | awk '{print $1}' | head -1 || true)
echo "   $DOMAIN -> ${RESOLVED:-introuvable}"
[ -n "$RESOLVED" ] || { echo "ERREUR : le domaine n'existe pas encore dans le DNS."; exit 1; }

set_env() {
  local key="$1" value="$2"
  if grep -q "^${key}=" .env; then sed -i "s|^${key}=.*|${key}=${value}|" .env; else echo "${key}=${value}" >> .env; fi
}
# Le domaine s'ajoute aux hôtes autorisés sans retirer l'IP.
HOSTS=$(grep '^DJANGO_ALLOWED_HOSTS=' .env | cut -d= -f2- || true)
case ",${HOSTS}," in *",${DOMAIN},"*) ;; *) set_env DJANGO_ALLOWED_HOSTS "${DOMAIN},${HOSTS:-localhost,127.0.0.1}";; esac
set_env DJANGO_CSRF_TRUSTED_ORIGINS "https://${DOMAIN}"
set_env WAGTAILADMIN_BASE_URL "https://${DOMAIN}"
set_env DJANGO_HTTPS "true"

echo ">> étape 1 : nginx en HTTP + défi Let's Encrypt"
set_env NGINX_CONF "nginx-http.conf"
docker compose up -d
docker compose up -d --force-recreate nginx
sleep 5
docker run --rm -v "$(docker volume ls -q | grep -m1 letsencrypt)":/etc/letsencrypt \
  -v "$(docker volume ls -q | grep -m1 certbot_www)":/var/www/certbot \
  certbot/certbot certonly --webroot -w /var/www/certbot -d "$DOMAIN" \
  --email "$EMAIL" --agree-tos --no-eff-email --non-interactive

echo ">> étape 2 : nginx en HTTPS"
sed "s/__DOMAIN__/${DOMAIN}/g" backend/deploy/nginx-https.conf > backend/deploy/nginx-https.generated.conf
set_env NGINX_CONF "nginx-https.generated.conf"
docker compose up -d --force-recreate web nginx
sleep 8
curl -sI "https://${DOMAIN}/fr/" | head -3 || echo "(test HTTPS local impossible : vérifiez depuis un navigateur)"
echo "Terminé : https://${DOMAIN}/fr/"
echo "Renouvellement automatique : ajoutez au crontab (sudo crontab -e) :"
echo "  0 3 * * * cd $(pwd) && bash backend/deploy/renew.sh >> /var/log/pad-renew.log 2>&1"
