# Contexte projet — Site du Port Autonome de Dakar (PAD)

> Ce fichier est lu automatiquement par Claude Code (VS Code / terminal) au
> début de chaque session. Il fixe le contexte, les conventions et l'objectif
> courant. **Tiens-le à jour** : c'est la mémoire du projet.

## Objectif

Refonte du site institutionnel **portdakar.sn** (actuellement Drupal 7, en fin
de vie) sur un socle **Python / Django 5 + Wagtail 6**. Public : usagers,
armateurs et croisiéristes internationaux, prestataires, candidats, agents.
Site bilingue **FR / EN**.

## Stack & versions

- Python 3.12, Django 5.1, Wagtail 6.3
- PostgreSQL en prod (SQLite en dev par défaut), Redis (cache/Celery à venir)
- Front : gabarits Django/Wagtail rendus serveur + **HTMX** + Alpine.js
  (amélioration progressive), design system CSS à base de tokens
- Déploiement : Docker / docker-compose, CI GitHub Actions

## Architecture (à respecter)

Découpage en **apps métier autonomes** sous `apps/` (un domaine = une app) :

| App | Rôle |
|-----|------|
| `core` | Socle : blocs de contenu réutilisables, vues transverses, design system |
| `cms` | Pages éditoriales Wagtail (HomePage, StandardPage) |
| `services` | Offre de service (accueil navires, passagers, marchandises, agréments) |
| `navires` | Mouvement des navires (arrivées, départs, à quai, marées, croisières) |
| `marches` | Marchés publics (appels d'offres, attributions, plan de passation) |
| `espace_pro` | Comptes, auth, SSO vers le portail de service |
| `recrutement` | Métiers, appels à candidature, postuler en ligne |
| `qualite` | Certifications ISO 9001/14001/45001 (snippet en place) |
| `api` | DRF : exposition/consommation de données, intégrations |

L'arborescence éditoriale cible est documentée dans
[`docs/architecture-navigation.md`](docs/architecture-navigation.md). Elle
organise le site autour de « Nous découvrir », « Nos services »,
« Opportunités d'affaires », « Espace média », « Infos pratiques »,
« Engagements » et « Espace Pro et recrutement ».

**Règles de découplage** : les dépendances pointent vers `core`, jamais en
croisé entre apps métier. Communication par services applicatifs / signaux, pas
d'accès direct aux modèles d'une autre app.

### Trois niveaux de modularité
1. **Applicatif** — apps découplées, settings par environnement, feature flags.
2. **Contenu** — `StreamField` Wagtail : bibliothèque de blocs dans
   `apps/core/blocks.py`. Un rédacteur compose sans développeur.
3. **Présentation** — tokens CSS dans `static/css/design-system.css`.

## Conventions de code

- **Français** pour le contenu, les libellés admin (`verbose_name`,
  `help_text`, `label`) et les commentaires ; anglais pour le code (noms de
  variables, fonctions).
- Qualité (doit passer avant tout commit) : `ruff check .`, `black .`,
  `pytest`. Config dans `pyproject.toml`. Le CI applique ces mêmes barrières.
- Migrations : toujours committer les fichiers de migration générés.
- **Accessibilité (RGAA/WCAG AA) non négociable** : HTML sémantique, un seul
  `h1` par page, `alt` obligatoire sur les images, focus visible, navigation
  clavier. Toute nouvelle page/gabarit respecte ça.
- **Sécurité** : aucun secret dans le code (variables d'environnement) ; ne pas
  affaiblir les réglages de `config/settings/prod.py`.
- i18n : envelopper les chaînes visibles dans `{% translate %}` / `gettext`.

## Commandes

```bash
source .venv/bin/activate
python manage.py migrate
python manage.py runserver          # site /fr/ , admin /admin/
python manage.py createsuperuser
make test | make lint | make format
```

## État actuel

- Socle en place : le projet démarre, l'admin Wagtail fonctionne, i18n FR/EN,
  en-têtes de sécurité, chaîne qualité, Docker/CI.
- Le socle SEO, la charte PAD AGORA, la navigation principale, les pages
  `services`, `navires`, `marches`, l'app éditoriale `media`, la page QSSE de
  `qualite`, le recrutement et l'espace pro sont implémentés et testés.
- L'arborescence cible de migration est formalisée dans
  `docs/architecture-navigation.md`.
- Le plan du site réel a été comparé à cette arborescence; ses sous-rubriques
  métier et les anciennes URL techniques sont inventoriées dans le document.
- La page d'accueil doit être définie comme racine du site Wagtail si une
  installation conserve encore la page « Welcome to your new Wagtail site! ».

## Tâches prioritaires (dans l'ordre)

1. Créer les pages racines de l'arborescence cible et les définir comme
  racine/menu dans Wagtail.
2. Compléter la couverture des pages Services et Infos pratiques selon le
  sitemap réel (pilotage, remorquage, marées, météo, formalités, etc.).
3. Écrire les scripts de reprise de contenu depuis Drupal 7 avec les slugs
  de `docs/architecture-navigation.md`.
4. Ajouter les redirections des anciennes URL `/node/`, `/content/` et
  `/viewpdf` vers les nouvelles pages lisibles.
5. Compléter le bilinguisme éditorial FR/EN.

## Comment me donner une tâche

Sois concret : « Développe l'app `navires` selon la tâche 2 du CLAUDE.md :
modèle Escale, page de liste filtrable HTMX, tests. Respecte les conventions
d'accessibilité et la chaîne qualité. » Puis relis le diff avant d'accepter.
