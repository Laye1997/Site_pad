# Prompts de refonte — Site du Port Autonome de Dakar

Prompts prêts à coller dans **Claude Code** (VS Code), une brique à la fois.
Garde ce fichier à la racine du projet (`pad-site/PROMPTS.md`).

## Mode d'emploi

Pour chaque étape :
1. Copie le bloc **« Prompt »** et colle-le dans le chat Claude Code.
2. Quand il a fini : **relis le diff**, puis clique **Keep** (ou **Undo** si ça ne va pas).
3. Vérifie dans le navigateur sur `localhost:8000`.
4. **Commit git** avec le message suggéré (pour pouvoir revenir en arrière).
5. Passe à l'étape suivante.

Règle d'or : **une brique à la fois**. Ne colle pas deux prompts d'un coup.

Rappels valables pour tous les prompts : respecter le `CLAUDE.md`, l'accessibilité
(RGAA/WCAG AA), le design system (`static/css/design-system.css`), l'i18n
(`{% translate %}`), et faire passer `ruff`, `black` et `pytest` avant de finir.

---

## Étape 0 — Petites corrections rapides

**Prompt :**
> Trois corrections rapides, sans rien casser d'autre :
> 1. Remplace partout la faute « TRAFFIC » par « TRAFIC » (orthographe française correcte), dans les gabarits de l'app `navires`.
> 2. Vérifie que la commande `python manage.py seed_navires` insère bien des escales d'exemple couvrant les trois statuts (attendu, à quai, parti), afin que chaque filtre affiche des données.
> 3. Assure-toi que le lien « Navires » du menu et le bouton « Voir le mouvement des navires » de l'accueil pointent bien vers la page `/navires/`.
> Fais passer `ruff`, `black` et `pytest`.

**Commit :** `fix: corrections orthographe et navigation navires`

---

## Étape 1 — App `services` (offre de service)

**Prompt :**
> Développe l'app `services` (offre de service) selon l'architecture du `CLAUDE.md`.
> - Crée un type de page Wagtail `ServicePage` : titre, résumé court, contenu en `StreamField` réutilisant les blocs de `apps/core/blocks.py`, et une illustration optionnelle (avec `alt` **obligatoire**).
> - Crée une page `ServiceIndexPage` qui liste ses `ServicePage` enfants sous forme de cartes accessibles.
> - Prévois les 4 services clés : accueil navires, trafic passagers, marchandises, obtention d'agrément.
> - Respecte l'accessibilité, le design system et l'i18n.
> - Ajoute des tests (rendu de l'index, rendu d'une fiche service).
> - Fais passer `ruff`, `black`, `pytest`, puis explique-moi comment créer ces pages dans l'admin et les voir sur le site.

**Commit :** `feat: app services (offre de service)`

---

## Étape 2 — App `marches` (marchés publics)

**Prompt :**
> Développe l'app `marches` (marchés publics) selon le `CLAUDE.md`.
> - Modèle `AppelOffre` : objet, référence, type (appel d'offres / avis d'attribution / plan de passation), date de publication, date limite de dépôt, document(s) attaché(s) (Wagtail documents), statut (ouvert / clôturé / attribué). Éditable dans l'admin Wagtail.
> - Page publique `/marches/` : liste filtrable par type et par statut (liens qui marchent sans JS, améliorés en HTMX), triée par date, avec téléchargement des documents.
> - Accessibilité (tableau ou liste avec structure correcte), design system, i18n.
> - Ajoute une commande `seed_marches` avec des exemples et des tests.
> - Fais passer `ruff`, `black`, `pytest`, puis montre-moi comment tester.

**Commit :** `feat: app marches (marchés publics)`

---

## Étape 3 — App `qualite` (certifications ISO & QSE)

**Prompt :**
> Complète l'app `qualite` selon le `CLAUDE.md` (le modèle `Certification` existe déjà).
> - Crée une page Wagtail `PageQSE` (Qualité, Sécurité, Environnement) : engagements, politique qualité, démarche RSE en `StreamField`.
> - Affiche sur cette page les certifications ISO 9001 / 14001 / 45001 (référentiel, périmètre, organisme, dates de validité, lien vers le certificat PDF), avec un indicateur visuel « en cours de validité / expirée » basé sur la propriété `est_valide`.
> - Crée un bloc de contenu réutilisable « certifications » (dans `apps/core/blocks.py`) pour pouvoir afficher les certificats sur n'importe quelle page.
> - Ajoute une tâche (commande de gestion) qui liste les certificats expirant dans moins de 60 jours, pour alerte.
> - Accessibilité, design system, i18n, tests. Fais passer `ruff`, `black`, `pytest`.

**Commit :** `feat: page QSE et affichage des certifications ISO`

---

## Étape 4 — App `recrutement` (carrières)

**Prompt :**
> Développe l'app `recrutement` selon le `CLAUDE.md`.
> - Modèle `Offre` : intitulé du poste, direction/service, type de contrat, description en `StreamField`, date de publication, date limite de candidature, statut (ouverte / clôturée).
> - Page `/recrutement/` : présentation des métiers portuaires + liste des offres ouvertes.
> - Un formulaire « Postuler en ligne » (nom, e-mail, message, pièce jointe CV) qui envoie un e-mail à un service RH configurable ; protège-le contre le spam et valide le type/taille de la pièce jointe.
> - Accessibilité (formulaire correctement étiqueté, messages d'erreur clairs), design system, i18n, tests. Fais passer `ruff`, `black`, `pytest`.

**Commit :** `feat: app recrutement (offres + candidature en ligne)`

---

## Étape 5 — App `espace_pro` (comptes & portail)

**Prompt :**
> Développe l'app `espace_pro` selon le `CLAUDE.md`.
> - Mets en place l'authentification des professionnels (connexion / déconnexion / réinitialisation de mot de passe) avec les vues d'auth de Django, dans la charte du site.
> - Crée une page d'espace pro protégée (accessible seulement connecté) affichant un tableau de bord simple.
> - Prépare le point d'accroche pour un futur SSO vers le portail de service (documente où le brancher, sans l'implémenter).
> - Sécurité : ne pas affaiblir les réglages de `config/settings/prod.py`, respecter les protections Django par défaut.
> - Accessibilité, design system, i18n, tests. Fais passer `ruff`, `black`, `pytest`.

**Commit :** `feat: app espace_pro (authentification professionnelle)`

---

## Étape 6 — SEO & Open Graph

**Prompt :**
> Ajoute la gestion SEO au site.
> - Active `wagtail.contrib.settings` (ou le module Metatag) pour définir un titre, une méta-description et une **image Open Graph par défaut** au niveau du site.
> - Sur chaque page, génère les balises `<meta name="description">`, `og:title`, `og:description`, `og:image`, `og:type`, `og:url` et les Twitter Cards, en réutilisant l'image de l'article/page quand elle existe, sinon l'image par défaut.
> - Ajoute une balise `canonical` et un `sitemap.xml` (via `django.contrib.sitemaps` / Wagtail).
> - Mets à jour les tests SEO. Fais passer `ruff`, `black`, `pytest`.

**Commit :** `feat: SEO, Open Graph et sitemap`

---

## Étape 7 — Contenu bilingue (i18n FR / EN)

**Prompt :**
> Mets en place la traduction du contenu FR / EN.
> - Installe et configure `wagtail-localize` pour traduire les pages Wagtail par langue.
> - Compile les traductions des chaînes d'interface (`makemessages` / `compilemessages`) pour FR et EN.
> - Vérifie que le sélecteur FR/EN de l'en-tête pointe vers la bonne version de la page courante.
> - Explique-moi comment créer la version anglaise d'une page dans l'admin. Fais passer `ruff`, `black`, `pytest`.

**Commit :** `feat: contenu bilingue FR/EN (wagtail-localize)`

---

## Étape 8 — Reprise du contenu Drupal 7

**Prompt :**
> Prépare la reprise du contenu depuis l'ancien site Drupal 7.
> - Écris une commande de gestion `import_drupal` qui lit un export (CSV ou JSON) des actualités et pages, et crée les pages Wagtail correspondantes (titre, corps converti en blocs, date, image).
> - Gère les cas d'erreur (champ manquant, image absente) sans planter, avec un rapport en fin d'exécution.
> - Ne touche pas aux données existantes déjà saisies à la main (idempotence : ne pas recréer une page déjà importée).
> - Documente le format d'export attendu. Ajoute des tests sur un petit échantillon. Fais passer `ruff`, `black`, `pytest`.

**Commit :** `feat: script de reprise du contenu Drupal 7`

---

## Après chaque étape

- Vérifie le site sur `localhost:8000/fr/`.
- `python manage.py migrate` si de nouveaux modèles ont été ajoutés.
- Commit git, et de temps en temps `git push` vers un dépôt distant (sauvegarde).
- Mets à jour le `CLAUDE.md` (section « État actuel ») quand une brique est terminée.
