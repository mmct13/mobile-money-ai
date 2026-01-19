# 🎭 Scénarios de Démonstration - MoneyShield CI

Ce document présente des mises en situation réalistes (Use Cases) pour démontrer la puissance de **MoneyShield CI** lors d'un pitch. Chaque scénario utilise des contextes locaux ivoiriens.

---

## 1. Le "Brouteur" de Yopougon (Cybercriminalité)
**Motif Détecté :** `Broutage`  
**Confiance IA :** 92%

### 📖 L'Histoire
Il est **3h du matin**. À **Yopougon-Niangon**, un individu tente de transférer **500,000 FCFA** depuis le compte d'une victime vers un compte Wave, en utilisant l'application mobile. C'est le classique "brouteur" qui profite du sommeil de sa victime.

### ⚙️ Ce que MoneyShield voit (Backend)
- **Heure :** 03:14 (Anomalie forte)
- **Montant :** 500,000 FCFA (Élevé)
- **Canal :** APP (Smartphone)
- **Lieu :** Abidjan-Yopougon (Zone à risque historique)

### 🛡️ Réaction du Système
> 🚨 **ALERTE BLOQUANTE** : Transaction suspendue.
> **Raison :** Combinaison critique [Nuit + Montant Élevé + Zone Suspecte].
> **Action :** Demande de validation biométrique ou appel de vérification.

---

## 2. Le "Schtroumpfage" à Adjamé (Accumulation Suspecte)
**Motif Détecté :** `Accumulation Suspecte`  
**Confiance IA :** 85%

### 📖 L'Histoire
**Moussa**, commerçant au Black Market d'Adjamé, essaie de blanchir de l'argent sale sans attirer l'attention. Au lieu de déposer 2 Millions d'un coup, il demande à 4 "petits" de faire des dépôts de **450,000 FCFA** chacun sur son compte en l'espace de **40 minutes**.

### ⚙️ Ce que MoneyShield voit (Backend)
- **Pattern :** 4 dépôts successifs sur le même compte `0505XXXXXX`.
- **Montant Cumulé :** 1,800,000 FCFA en < 1h.
- **Vitesse :** Transactions rapprochées (Vélocité anormale).

### 🛡️ Réaction du Système
> ⚠️ **ALERTE D'INVESTIGATION** : Compte flaggé pour Structuring.
> **Raison :** Règle `RegleSchtroumpfage` déclenchée. Tentative de contourner les seuils de vigilance.
> **Action :** Signalement au service conformité (Compliance).

---

## 3. Le SIM Swap de l'Homme d'Affaires
**Motif Détecté :** `SIM Swap`  
**Confiance IA :** 98%

### 📖 L'Histoire
**M. Kouassi**, DG d'une PME au Plateau, perd soudainement le réseau sur son téléphone vers **10h00**. À **10h15**, une tentative de vidage de son compte Orange Money (**2,500,000 FCFA**) est initiée par code USSD. Les fraudeurs ont cloné sa carte SIM avec la complicité d'un agent véreux.

### ⚙️ Ce que MoneyShield voit (Backend)
- **Canal :** USSD (Typique après swap).
- **Montant :** Très élevé (Max du plafond journalier).
- **Contexte :** Changement récent d'IMSI (Identifiant carte SIM) détecté par l'opérateur.

### 🛡️ Réaction du Système
> ⛔ **BLOCAGE IMMÉDIAT** : Compte gelé.
> **Raison :** Risque maximal de prise de contrôle du compte (Account Takeover).
> **Action :** Le client doit se présenter en agence physique avec sa CNI.

---

## 4. L'Arnaque "Gagnoa n'est pas loin" (Ingénierie Sociale)
**Motif Détecté :** `Ingénierie Sociale`  
**Confiance IA :** 75%

### 📖 L'Histoire
**Tantie Awa** reçoit un appel insistant : *"Maman, c'est le gérant de la compagnie de car, ton colis est arrivé mais il faut payer 5,000 FCFA de frais de dossier sinon ça repart !"*. Paniquée, elle s'apprête à envoyer l'argent rapidement.

### ⚙️ Ce que MoneyShield voit (Backend)
- **Montant :** Faible/Moyen (5,000 - 50,000 FCFA).
- **Destinataire :** Numéro nouvellement activé ou signalé pour arnaques.
- **Comportement :** La victime compose le code USSD très lentement (guidée au téléphone) ou hésite.

### 🛡️ Réaction du Système
> 📱 **POP-UP PRÉVENTIF** : Message sur l'écran d'Awa.
> **Message :** *"Attention, ne payez jamais de frais pour un lot ou un colis inconnu. Êtes-vous sûre de connaître ce numéro ?"*
> **Action :** Friction positive pour briser la manipulation psychologique.

---

## 5. Le "Gbaka" de Blanchiment (Zones Rurales)
**Motif Détecté :** `Blanchiment`  
**Confiance IA :** 80%

### 📖 L'Histoire
À **Soubré** (zone cacaoyère), un compte inactif depuis 6 mois reçoit soudainement **5,000,000 FCFA** puis tente de tout retirer en espèces via un agent dans l'heure qui suit. C'est une "mule" utilisée pour sortir l'argent du circuit numérique.

### ⚙️ Ce que MoneyShield voit (Backend)
- **Ville :** Soubré (Zone à surveillance accrue hors période de traite).
- **Flux :** In/Out immédiat (Passoire).
- **Montant :** Massif pour un profil "Dormant".

### 🛡️ Réaction du Système
> 🕵️ **ALERTE LBC (Lutte Blanchiment Capitaux)**.
> **Raison :** Mouvement de fonds atypique incohérent avec le profil client.

---

## 6. Le Harcèlement / Spam (Vélocité)
**Motif Détecté :** `Vélocité Excessive`  
**Confiance IA :** 88%

### 📖 L'Histoire
Un utilisateur envoie **15 transferts** de 100 FCFA à la suite vers le même numéro en l'espace de **5 minutes**, probablement pour saturer la boîte de réception SMS de la victime ou faire passer un message insistant via les descriptions de transfert.

### ⚙️ Ce que MoneyShield voit (Backend)
- **Fréquence :** > 10 transactions / 5 min.
- **Montant :** Insignifiant.
- **Répétition :** Même pair Expéditeur/Destinataire.

### 🛡️ Réaction du Système
> 🛑 **TEMPORISATION** : Compte temporairement restreint d'envoi.
> **Raison :** Comportement robotique ou abusif.

---

## 7. La Prévision de Trésorerie (Use Case Business)
**Fonctionnalité :** `Dashboard Financier`
**Objectif :** Anticipation de liquidités

### 📖 L'Histoire
Le **Directeur Financier** de la banque partenaire souhaite savoir combien de liquidités doivent être mises à disposition des agents pour le week-end de Pâques à venir. Il consulte le nouveau Dashboard.

### ⚙️ Ce que MoneyShield voit (Backend)
- **Historique :** Analyse des volumes horaires des 7 derniers jours.
- **Tendance :** Le modèle de régression linéaire détecte une hausse progressive de 15% des volumes chaque vendredi soir.

### 🛡️ Apport du Système
> 📈 **PRÉVISION IA** : Courbe prédictive affichée sur 24h.
> **Insight :** Le système prévoit un pic de volume à **200 Millions FCFA** demain à 18h.
> **Action :** Provisionnement anticipé des comptes Master-Agent pour éviter les pénuries de cash (e-money).
