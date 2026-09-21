# Site du Port Autonome de Dakar — socle Django + Wagtail

Squelette applicatif de la refonte de **portdakar.sn**, conforme à la note
d'architecture cible : socle **Python / Django 5 + Wagtail 6**, découpage en
apps métier, design system à base de tokens, internationalisation FR/EN,
et outillage qualité / CI / Docker.

> Statut : **starter de Phase 0**. Le projet démarre, l'admin fonctionne, les
> mécanismes structurants sont en place. Les fonctionnalités métier restent à
> développer app par app.

## Démarrage rapide (développement)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements/dev.txt

cd backend
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

- Site : http://localhost:8000/fr/
- Administration Wagtail : http://localhost:8000/admin/
- Sonde de santé : http://localhost:8000/healthz/

Par défaut, la base est **SQLite** (aucune installation requise). En production,
renseignez `DATABASE_URL` pour basculer sur **PostgreSQL**.

## Avec Docker (proche de la production)

```bash
docker compose up --build
# web + PostgreSQL + Redis
```

## Structure du projet

```
backend/           Tout le Python (commandes à lancer depuis ce dossier)
  manage.py
  config/          Réglages (settings/base·dev·prod), urls, wsgi/asgi
  apps/
    core/          Socle : blocs de contenu réutilisables, vues transverses
    cms/           Pages éditoriales Wagtail (HomePage, StandardPage)
    services/      Offre de service
    navires/       Mouvement des navires, croisières
    marches/       Marchés publics
    espace_pro/    Espace professionnel / SSO
    recrutement/   Carrières
    qualite/       Certifications ISO 9001/14001/45001
    media/         Espace média (actualités)
    api/           API & intégrations (DRF)
  locale/          Traductions FR / EN
  requirements/    base / dev / prod
  data/            Documents importés par les commandes de contenu (PDF agréments)
  deploy/          Scripts de déploiement (deploy.sh, https.sh) et configurations nginx
  docs/            Architecture, ADR, prompts
  sources/         Matériaux bruts de l'ancien site (hors image Docker)
  Makefile         make test / lint / run (à lancer depuis backend/)
frontend/          Tout le visuel
  templates/       Gabarits HTML : base.html, includes/ puis un dossier par app (cms/, navires/…)
  static/          css/design-system.css (tokens), js/, img/, fonts/, video/
(racine : backend/, frontend/, Dockerfile et docker-compose.yml ; le reste est dans des dossiers cachés)
```

Chaque app métier est un **module autonome** (bounded context) : ses modèles,
vues, gabarits, tests et migrations lui appartiennent. Les dépendances pointent
vers `core`, jamais en croisé entre apps métier.

## Ce qui est déjà en place

- **Modularité applicative** — 9 apps découplées, réglages par environnement.
- **Modularité de contenu** — `StreamField` avec une bibliothèque de blocs
  (titre, texte, image *avec alt obligatoire*, encadré, bouton) : le rédacteur
  compose ses pages sans développeur.
- **Modularité de présentation** — design system à base de tokens CSS.
- **Accessibilité** — lien d'évitement, focus visible, `lang` déclaré, alt
  obligatoire sur les images, HTML sémantique.
- **i18n FR/EN** — préfixes de langue `/fr/` `/en/`, Wagtail multilingue activé.
- **Sécurité** — en-têtes durcis, HSTS/cookies sécurisés et CSP en prod,
  secrets par variables d'environnement.
- **Qualité** — `ruff`, `black`, `mypy`, `pytest` + pipeline CI GitHub Actions.
- **Certifications ISO** — modèle `Certification` (référentiel, périmètre,
  organisme, dates de validité, PDF) géré depuis l'admin.

## Prochaines étapes suggérées

1. Créer la page d'accueil dans l'admin et la définir comme racine du site.
2. Développer l'app `navires` (premier service à forte valeur d'usage).
3. Écrire les scripts de reprise de contenu depuis Drupal 7.
4. Brancher l'authentification de l'espace pro (SSO portail de service).

## Commandes utiles

```bash
make run       # serveur de développement
make test      # tests
make lint      # ruff + black --check
make format    # corrige le style automatiquement
make super     # créer un compte administrateur
```

---
Socle généré comme point de départ de la refonte — à faire évoluer selon les
décisions de cadrage (Phase 0).
