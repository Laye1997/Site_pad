# ADR 0001 — Découplage des apps métier par services applicatifs

**Statut** : accepté — 19/09/2026

## Contexte
Le cahier d'architecture impose des apps métier autonomes : dépendances vers `core`, jamais croisées,
sans accès direct aux modèles d'une autre app.

## Décision
Chaque app expose un module `services.py` (interface stable, retours simples : listes, dicts).
`cms` (accueil) et `api` consomment `navires.services`, `media.services` et `qualite.services` ;
ils n'importent jamais les modèles de ces apps.

## Conséquences
On peut refondre `navires` (ex. alimentation AIS) sans toucher à l'accueil ou à l'API tant que les
signatures des services sont respectées. Les services sont testés isolément.
