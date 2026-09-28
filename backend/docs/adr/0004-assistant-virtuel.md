# ADR 0004 — Assistant virtuel (chatbot) limité au Port Autonome de Dakar

**Statut** : proposé — 28/09/2026

## Contexte
Le PAD souhaite une fenêtre de discussion flottante (à la manière de dpworld.com) qui renseigne les
visiteurs sur le port, et uniquement sur le port.

## Décision
- App `apps/assistant`, point d'entrée `POST /assistant/chat/`, widget `includes/assistant.html`
  + `static/js/assistant.js` + `static/css/assistant.css` (aucun code inline, cf. ADR 0002).
- **Sources** : les pages Wagtail publiées (relues à chaque publication), les rubriques servies par des
  vues (navires, marchés, recrutement), une FAQ éditoriale `data/assistant/faq.md`, et le mouvement des
  navires via `apps.navires.services` (cf. ADR 0001). Recherche BM25 en mémoire : pas de base vectorielle.
- **Modèle** : API OpenAI (Chat Completions, streaming), modèle réglable par `ASSISTANT_MODEL`
  (défaut `gpt-4.1-mini`). Toute API compatible OpenAI est possible via `ASSISTANT_BASE_URL`.
- **Périmètre** : consigne système stricte (réponse fixe hors sujet, interdiction d'inventer, renvoi
  vers le numéro vert). Les pages utilisées sont proposées en liens sous la réponse.
- **Sécurité et coûts** : feature flag `FEATURE_ASSISTANT` (actif si `OPENAI_API_KEY` est définie),
  requêtes de même origine uniquement, quotas par IP (8/min, 80/jour) et global (3 000/jour),
  réponses plafonnées à 600 tokens, messages tronqués à 1 000 caractères.
- **Données personnelles** : les messages ne sont ni journalisés ni stockés côté serveur ; la
  conversation vit dans `sessionStorage` (onglet courant). Le widget avertit l'usager que ses messages
  sont transmis au prestataire d'IA.
- **Exploitation** : gunicorn passe à `--threads 4` pour qu'une réponse en streaming n'immobilise pas un
  processus ; nginx transmet le flux sans tampon grâce à l'en-tête `X-Accel-Buffering: no`.

## À valider par le PAD
- Recours à un prestataire d'IA hors UE/Sénégal (OpenAI) : mention au registre des traitements et dans
  la politique de confidentialité ; alternative possible (Mistral AI, Azure OpenAI région UE).
- Plafond de dépense mensuel à fixer sur le compte du prestataire.
