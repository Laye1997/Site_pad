# ADR 0002 — CSP stricte : aucun script ni style inline sur le site public

**Statut** : accepté — 19/09/2026

## Décision
La production applique `script-src 'self'` et `style-src 'self'` (django-csp). Tous les scripts vivent
dans `static/js/`. Les données structurées JSON-LD (non exécutables) sont permises. L'admin Wagtail,
qui utilise des scripts inline, est exclu de la politique (`EXCLUDE_URL_PREFIXES`).

## Conséquences
Un test (`apps/core/tests.py`) échoue si un script ou un style inline est réintroduit.
Le menu principal reste utilisable sans JavaScript (amélioration progressive).
