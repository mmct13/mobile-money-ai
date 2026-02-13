# GUIDE DE DÉMONSTRATION - MONEYSHIELD CI

Ce guide détaille les étapes pour réaliser une démonstration complète et percutante du projet MoneyShield CI, en partant d'une base neuve.

## 1. Préparation (Reset Total)

Avant de commencer la présentation, assurez-vous que l'environnement est propre.

1.  **Exécuter** `reset_app.bat`.
    - Cela va :
        - Arrêter tous les conteneurs Docker.
        - Supprimer la base de données (`moneyshield.db`).
        - Supprimer les modèles IA entraînés (`.pkl`).
    - **À la fin**, le script vous demandera si vous voulez relancer l'application. Répondez **O (Oui)** pour lancer `start_app.bat` automatiquement.

*Si vous avez répondu Non, lancez manuellement `start_app.bat`.*

---

## 2. Démarrage et Initialisation

Laissez le script `start_app.bat` tourner. Il va :
1.  Créer l'environnement virtuel (si nécessaire).
2.  Initialiser une nouvelle base de données vide.
3.  **Entraîner le modèle IA** sur les données de base (puisque les précédents ont été supprimés).
4.  Lancer les conteneurs Docker (Kafka, API, Dashboard...).

> **Note :** Attendez que le Dashboard s'ouvre dans votre navigateur (http://localhost:8501).

---

## 3. Injection de Données Passées (Contexte)

Pour ne pas présenter un tableau de bord vide, nous allons simuler une activité "normale" sur les 2-3 derniers jours.

1.  **Exécuter** `inject_past.bat`.
    - Cela va générer des transactions datées d'il y a 48h à 24h.
2.  **Rafraîchir** la page du Dashboard.
    - Vous devriez voir des courbes d'activité apparaître dans l'historique, donnant l'impression que le système tourne depuis quelques jours.

---

## 4. Démonstration Temps Réel

Le système est maintenant "en vie".

1.  Montrez le **Dashboard**. Expliquez les KPIs (Volume, Montant, Fraudes détectées).
2.  Le générateur de transactions (`generator` container) tourne en arrière-plan et envoie des transactions en temps réel.
    - Vous pouvez voir le compteur "Transactions récentes" augmenter petit à petit.

---

## 5. Simulation d'Attaque (Le "Wow" Effect)

C'est le moment de tester la réactivité du système face à une fraude complexe.

1.  Gardez le Dashboard ouvert et visible.
2.  **Exécuter** `inject_scenario.bat`.
    - **Scénario** : Un retrait massif (2.000.000 FCFA) effectué à **Korhogo** (Nord) à **03h00 du matin**, alors que l'abonné habite habituellement à Abidjan et que l'heure est suspecte.
3.  **Observez le Dashboard** :
    - Une nouvelle alerte rouge devrait apparaître dans le tableau "Dernières Alertes".
    - Le compteur "Montant Fraude" va bondir.
    - Cliquez sur l'onglet **"Exploration des Données"** ou **"Alertes"** (si disponible) pour voir les détails de la transaction frauduleuse (Score de risque élevé, Motif : "Montant anormal", "Horaire suspect", etc.).

---

## Résumé des Commandes

| Étape | Script à lancer | Description |
| :--- | :--- | :--- |
| **1. Nettoyage** | `reset_app.bat` | Remise à zéro (DB, Docker, Modèles). |
| **2. Démarrage** | `start_app.bat` | Lancement de l'infra et entraînement IA. |
| **3. Historique** | `inject_past.bat` | Injection de données J-3 à J-1. |
| **4. Attaque** | `inject_scenario.bat` | Simulation d'une fraude spécifique. |
