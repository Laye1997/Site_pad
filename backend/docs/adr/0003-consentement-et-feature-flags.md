# ADR 0003 — Consentement, traceurs et feature flags

**Statut** : accepté — 19/09/2026

## Décision
- Aucun traceur avant choix explicite : le bandeau (`frontend/static/js/consent.js`) stocke le choix dans
  `localStorage` (`pad_consent`) et émet l'événement `pad:consent`. Tout script de mesure d'audience
  devra s'abonner à cet événement.
- Les fonctions optionnelles se pilotent par variables d'environnement (`FEATURE_CONSENT_BANNER`,
  `FEATURE_PUBLIC_API`, `FEATURE_HOME_SHIP_MOVEMENT`), exposées via `settings.FEATURES`.

## À valider par le PAD
Durées de conservation, registre des traitements, textes des pages légales (brouillons créés par
`seed_legal_pages`, non publiés).
