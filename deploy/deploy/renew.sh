#!/usr/bin/env bash
# Renouvelle le certificat Let's Encrypt (à lancer chaque nuit par cron) puis recharge nginx.
set -euo pipefail
cd "$(dirname "$0")/.."
docker run --rm -v "$(docker volume ls -q | grep -m1 letsencrypt)":/etc/letsencrypt \
  -v "$(docker volume ls -q | grep -m1 certbot_www)":/var/www/certbot \
  certbot/certbot renew --webroot -w /var/www/certbot --quiet
docker compose exec -T nginx nginx -s reload
