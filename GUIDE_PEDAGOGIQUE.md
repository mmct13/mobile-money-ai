# 🎓 Comment ça marche ? Guide Pédagogique du Code Mobile-Money-AI

Bienvenue dans les coulisses de **MoneyShield CI** ! Ce document va vous expliquer comment tout ce système fonctionne, ligne par ligne ou presque, comme si nous étions en cours.

---

## 🌍 La Vue d'Ensemble : L'Architecture Pipeline

Imaginez une **usine de traitement de courrier**.
1.  Quelqu'un poste des lettres (**Le Générateur**).
2.  Un tapis roulant transporte ces lettres à toute vitesse (**Kafka**).
3.  Un inspecteur examine chaque lettre pour voir si elle est suspecte (**Le Détecteur**).
4.  Si c'est suspect, il l'affiche sur un écran de contrôle (**Le Dashboard**).

C'est exactement ce que fait notre code.

---

## 1. 🎭 Le Générateur (`app/generator/generateur.py`)
*C'est l'acteur qui simule la vie réelle.*

Son rôle est de créer de fausses transactions qui ressemblent à de vraies transactions Mobile Money en Côte d'Ivoire.

*   **La boucle infinie :** Il tourne sans arrêt (`while True`).
*   **Le profil "Normal" (96%) :** La plupart du temps, il crée une transaction banale : un retrait de 5000F à 14h.
*   **Le profil "Fraudeurs" (4%) :** De temps en temps, il joue un rôle de méchant :
    *   *Le Brouteur :* Il force l'heure à 3h du matin et le montant à 500,000F.
    *   *L'Agent Véreux :* Il fait des dépôts bizarres le soir.
*   **L'envoi :** Une fois la transaction créée (un dictionnaire Python `{...}`), il l'envoie dans le tuyau **Kafka**.

## 2. 📨 Le Messager (`Kafka` + `Zookeeper`)
*C'est le tapis roulant.*

Ce n'est pas du code Python que nous avons écrit, mais un logiciel qu'on utilise (via Docker).
*   **Topic :** C'est le nom du tuyau. Ici, il s'appelle `flux_mobile_money`.
*   **Rôle :** Il s'assure que si le Détecteur est un peu lent, les transactions ne sont pas perdues. Elles attendent sagement dans la file.

## 3. 🕵️ Le Cerveau : Le Détecteur (`app/detector/detecteur.py`)
*C'est l'inspecteur intelligent.*

C'est la partie la plus complexe. Il fait trois choses en même temps :

### A. L'Écoute
Il se connecte au "tapis roulant" Kafka et prend les transactions une par une (`for message in consumer`).

### B. L'Intelligence Artificielle (Le "Flair")
Il utilise un modèle appelé **Isolation Forest** (chargé depuis `modele_fraude.pkl`).
*   Imaginez que l'IA a vu 50,000 transactions normales. Elle sait à quoi ressemble la "normalité".
*   Quand une nouvelle transaction arrive, elle la compare. Si elle est trop différente (montant bizarre, heure bizarre), elle dit : *"Anomalie !"*.
*   **Problème :** L'IA dit juste "C'est bizarre", mais elle ne sait pas *pourquoi*. Elle ne sait pas dire "C'est un brouteur".

### C. Le Classificateur (`app/detector/classificateur_fraude.py`)
*C'est Sherlock Holmes.*

C'est ici qu'intervient notre code intelligent basé sur des règles. Si l'IA sonne l'alarme, le Classificateur entre en jeu avec sa loupe pour trouver le **Motif**.

Il possède une liste de règles (comme une check-list de police) :
*   **Règle Vélocité :** *"Est-ce que ce numéro a fait plus de 3 opérations en 15 minutes ?"* -> Si oui, score +40%.
*   **Règle Broutage :** *"Est-ce qu'il est 3h du matin ET que le montant est gros ?"* -> Si oui, score +80%.
*   **Règle Schtroumpfage :** *"Est-ce qu'on essaie de déposer 2 millions en petits morceaux ?"*

Il calcule le score pour chaque règle. Celle qui a le plus grand score gagne.
*   *Exemple :* Si la règle "Broutage" donne 90% et "Sim Swap" donne 10% -> Le motif est **BROUTAGE**.

Une fois identifié, il sauvegarde tout dans la Base de Données (`moneyshield.db`).

### D. Le Module Financier
Le système enregistre désormais **toutes** les transactions (et pas seulement les fraudes) dans une table dédiée. Cela nous permet de faire deux choses passionnantes :
1.  **Calculer les Volumes** : Savoir combien d'argent circule réellement.
2.  **Prédire l'Avenir** : Utiliser une régression linéaire simple pour estimer le volume des prochaines 24 heures.

## 4. 📊 L'Écran de Contrôle : Le Dashboard (`app/dashboard/dashboard.py`)
*C'est la télé pour les humains.*

C'est une interface web créée avec **Streamlit** (très facile pour faire des sites de data en Python).
*   Il lit la base de données `moneyshield.db`.
*   Il affiche les alertes en temps réel (Page Sécurité).
*   **NOUVEAU** : Il montre une **carte interactive de la Côte d'Ivoire** avec des bulles rouges pour identifier les zones critiques.
*   Il affiche les tendances financières et les prévisions (Page Finance).
*   Il dessine des graphiques (Camemberts, Courbes) pour montrer l'évolution de la fraude.
*   Il se rafraîchit automatiquement pour montrer les nouvelles données.

---

## 📝 Résumé du Parcours d'une Donnée

1.  **Générateur** : *"Je crée un faux retrait de 1M à 2h du matin."* -> Envoi Kafka.
2.  **Kafka** : Transporte le message.
3.  **Détecteur (IA)** : *"Oulah ! C'est pas normal ça (Score -0.8)."*
4.  **Détecteur (Classificateur)** : *"Analysons... 2h du matin + Gros montant = C'est du **Broutage** !"*
5.  **Détecteur (DB)** : *"J'écris ça dans le registre permanent avec le motif."*
6.  **Dashboard** : *"Ah, une nouvelle ligne dans le registre ! Je l'affiche en rouge sur l'écran du chef."*

Et voilà ! C'est un cycle continu qui protège les utilisateurs 24h/24. 🛡️
