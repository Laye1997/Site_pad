# Architecture éditoriale cible

Cette arborescence guide la reprise du contenu de `portdakar.sn` et la création des pages Wagtail. Elle conserve les rubriques utiles de l'ancien site tout en supprimant les URL techniques (`/node/`, `/content/`, `/viewpdf`, `/weather`).

Source de l'inventaire : [plan du site PAD](https://www.portdakar.sn/fr/sitemap), consulté le 19 septembre 2026.

## Navigation principale

1. **Nous découvrir**
   - Présentation
   - Position géographique
   - Historique
   - Infrastructures
   - Organisation : statut et mission, administration, assemblée générale, organigramme
   - Représentation commerciale
   - Nos chiffres clés
   - Démarche sécurité et sûreté
   - Visiter le port : demande de visite, visite virtuelle
   - Nos partenaires
   - Partenaires stratégiques, institutionnels et internationaux
   - Associations

2. **Nos services**
   - Accueil navires
   - Accès nautique et balisage
   - Pilotage
   - Remorquage
   - Lamanage
   - Avitaillement
   - Réparation navale
   - Entreprises agréées
   - Trafic passagers
   - Gare maritime
   - Dakar-Ziguinchor
   - Dakar-Gorée
   - Marchandises
   - Manutention
   - Stockage / entreposage
   - Enlèvement de marchandises

3. **Opportunités d'affaires**
   - Appels d'offres
   - Avis d'attribution
   - Procédures et agréments
   - Plan de passation
   - Manifestation d'intérêt

4. **Espace média**
   - Actualités
   - Publications : rapports, Tam Tam du Docker
   - Communiqués de presse
   - Photothèque
   - Vidéothèque
   - Pagination et catégories éditoriales

5. **Infos pratiques**
   - Prévisions du trafic
   - Croisières
   - Lignes régulières
   - Formalités : douane, taxes portuaires
   - Lexique
   - Heures de marées
   - Météo
   - Horaires
   - Contacts
   - Accès au port
   - FAQ
   - Plan du site

6. **Engagements**
   - RSE
   - QSSE
   - Certifications ISO

7. **Espace Pro et recrutement**
   - Connexion espace pro
   - Services en ligne
   - Appels à candidature
   - Candidature spontanée
   - Réclamation client

## Règles de migration

- Chaque page importée reçoit un slug lisible et stable, sans identifiant Drupal.
- Les anciens `/node/...` et `/content/...` sont réaffectés à une rubrique cible avant import.
- Les PDF sont des documents Wagtail téléchargeables directement; aucun visualiseur `/viewpdf` n'est reconduit.
- Le widget météo est remplacé par un composant métier météo/marée uniquement après validation de la source de données.
- Toutes les rubriques essentielles disposent d'une version anglaise prévue dans l'arborescence.
- Les pages sont publiées dans Wagtail avec « Afficher dans les menus » uniquement lorsqu'elles appartiennent à la navigation principale.
- Les slugs de la nouvelle version privilégient les formes courtes et stables :
   `nous-decouvrir`, `nos-services`, `opportunites-affaires`, `espace-media`,
   `infos-pratiques`, `engagements`, `espace-pro` et `recrutement`.
- Les anciennes variantes incohérentes sont normalisées : `marchandise` devient
   `marchandises`, `trafic-passager` devient `trafic-passagers`, et les fautes de
   casse ou d'accents sont corrigées dans les titres visibles.

## Correspondance avec les apps

| Rubrique | App ou modèle cible |
| --- | --- |
| Nous découvrir | `apps.cms.StandardPage` |
| Nos services | `apps.services.ServiceIndexPage` et `ServicePage` |
| Opportunités d'affaires | `apps.marches` |
| Espace média | future app éditoriale `media` |
| Infos pratiques | `apps.cms.StandardPage` et blocs réutilisables |
| RSE / QSSE | `apps.qualite.PageQSE` |
| Espace Pro | `apps.espace_pro` |
| Recrutement | `apps.recrutement` |

## Inventaire des composants à remplacer

| Ancien élément | Cible de la refonte |
| --- | --- |
| `/node/...` | Page Wagtail avec slug métier lisible et redirection permanente |
| `/content/...` | Réaffectation à la rubrique cible, sans dossier fourre-tout |
| `/viewpdf` | Lien direct vers un document Wagtail avec titre et taille |
| `/weather/...` | Composant météo/marées à brancher sur une source validée |
| `politique-surete-gmid` | Page métier sous `nos-services/trafic-passagers` ou `engagements` selon validation éditoriale |
| `10.3.0.13/...` | URL interne supprimée, jamais importée en production |
