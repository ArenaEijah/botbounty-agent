# BotBounty Agent

Agent expérimental pour rechercher, analyser et préparer des tâches BotBounty.

## Fonctionnalités

- Recherche périodique des bounties via l'API officielle BotBounty.
- Retry automatique sur les erreurs API temporaires.
- Historique des bounties déjà vues et détection des changements.
- Scoring par récompense, pertinence technique et effort estimé.
- Priorisation des opportunités.
- Contrôle de qualité des données.
- Vérification de l'éligibilité : récompense, statut, doublon et deadline.
- Revue renforcée des deadlines proches ou invalides.
- Évaluation de faisabilité et complétude des exigences.
- Génération de rapports Markdown et de statistiques de scan.
- Préparation de brouillons de solutions uniquement lorsque les exigences sont suffisamment complètes.
- Validation statique des brouillons sans exécuter de code généré.
- Tests automatisés exécutés par GitHub Actions toutes les 30 minutes, à chaque push sur main et manuellement.

## Sécurité

Le projet est actuellement **read-only / simulation**.

- Aucune clé privée, seed phrase ou secret crypto n'est stocké dans le dépôt.
- Les secrets éventuels passent uniquement par des variables d'environnement.
- Aucun claim automatique.
- Aucune soumission automatique.
- Aucun déploiement automatique.
- Aucun transfert ou paiement.
- Aucune opération de wallet.
- Les brouillons générés sont explicitement marqués comme non vérifiés.
- La validation des brouillons reste statique et n'exécute pas le code généré.

## Démarrage

```bash
python -m botbounty_agent
```

La configuration par défaut utilise l'API officielle BotBounty et le mode simulation.

## CI

Le workflow `.github/workflows/botbounty-scan.yml` :
1. installe les dépendances ;
2. exécute tous les tests ;
3. lance le scan read-only ;
4. publie le rapport et les brouillons comme artefacts.

## État du projet

La chaîne de recherche, analyse, filtrage, préparation et reporting est automatisée et couverte par la CI.

La partie financière et les actions irréversibles restent volontairement hors périmètre de cette version. Elles nécessiteraient une activation séparée, une gestion sécurisée des credentials et une validation humaine.
