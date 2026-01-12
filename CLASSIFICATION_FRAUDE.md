# Classification Intelligente des Fraudes - MoneyShield CI

## Vue d'ensemble

Le système de classification des motifs de fraude a été **complètement revu** pour éliminer la logique arbitraire des `if/elif` et la remplacer par un **système de scoring multi-critères intelligent**.

---

## Problème Initial

L'ancienne version utilisait une logique arbitraire et simpliste :

```python
# ❌ AVANT - Logique arbitraire
if transaction['montant'] > 1000000:
    motif = "Blanchiment suspecté"
elif heure < 6:
    motif = "Broutage / Intrusion nocturne"
elif transaction.get('canal') == "USSD":
    motif = "Ingénierie Sociale / SIM Swap USSD"
```

**Problèmes :**
- Conditions mutuellement exclusives (une seule règle peut s'appliquer)
- Ordre arbitraire des conditions
- Pas de nuances ni de score de confiance
- Difficile à maintenir et à améliorer

---

## Solution : Système de Scoring Multi-Critères

### Principe

Chaque type de fraude est représenté par une **règle** qui évalue la transaction selon plusieurs **critères**. Chaque critère ajoute un score partiel, et la règle avec le **meilleur score** est retenue.

### Architecture

```
classificateur_fraude.py
├── ClassificateurFraude       (Coordinateur principal)
├── RegleFraude                (Classe de base abstraite)
├── RegleBroutage              (Score: heure + montant + canal + opérateur)
├── RegleSimSwap               (Score: montant + canal + heure + type)
├── RegleBlanchiment           (Score: montant + ville + canal + type)
├── RegleIngenierieSociale     (Score: montant + canal + heure + type)
├── RegleVolPhysique           (Score: heure + montant + type+canal + ville)
├── RegleFraudeAgent           (Score: canal + heure + montant + type)
└── RegleAnomalieBehaviorale   (Règle par défaut)
```

---

## Types de Fraudes Détectables

### 1️⃣ Vélocité Excessive (Répétition Rapide)

**Description :** Multiples transactions sur le même numéro en peu de temps.
**Priorité :** 8/10
**Critères de détection :**
- ⏱️ > 3 transactions en 15 minutes : +40%
- ⏱️ > 5 transactions en 15 minutes : +40% (Total +80%)

### 2️⃣ Accumulation Suspecte (Schtroumpfage)

**Description :** Structuring : Dépôts multiples totalisant un montant élevé pour éviter les seuils.
**Priorité :** 9/10
**Critères de détection :**
- 💰 Somme cumulée > 1M XOF en moins d'1h : +50%
- 💰 Somme > 2M XOF : +30%
- 🔄 Nombre de transactions ≥ 3 : +20%

### 3️⃣ Broutage (Cybercriminalité Ivoirienne)

**Description :** Transactions nocturnes massives via smartphone  
**Priorité :** 9/10  
**Critères de détection :**
- ⏰ Heure nocturne (0h-6h) : +40%
- 💰 Montant > 200k XOF : +30% (+10% si > 500k)
- 📱 Canal APP ou CARTE : +20%
- 🟦 Opérateur Wave : +10%

**Exemple :**
```python
Transaction: 500k XOF, APP, Wave, 3h du matin
Score: 0.4 + 0.4 + 0.2 + 0.1 = 1.0 (100%)
Motif: Broutage
```

---

### 2️⃣ SIM Swap (Vol d'Identité)

**Description :** Prise de contrôle du compte via nouveau SIM  
**Priorité :** 10/10 (Très dangereux)  
**Critères de détection :**
- 💰 Montant > 500k : +30% (+20% si > 1M)
- 🏪 Canal AGENT : +30% (USSD : +20%)
- ⏰ Heure matinale 2h-7h : +20%
- 🔄 Type RETRAIT/TRANSFERT : +10%

---

### 3️⃣ Blanchiment d'Argent

**Description :** Flux financiers atypiques en zones non urbaines  
**Priorité :** 10/10  
**Critères de détection :**
- 💰 Montant > 1M : +40% (+20% si > 2M)
- 📍 Zones sensibles (San-Pédro, Soubré, etc.) : +30%
- 🏪 Canal AGENT : +20%
- 🔄 Type DEPOT : +10%

---

### 4️⃣ Ingénierie Sociale (Phishing/Vishing)

**Description :** Arnaques par SMS/Appels (faux gains, faux frais)  
**Priorité :** 7/10  
**Critères de détection :**
- 💰 Montant modéré (50k-300k) : +30%
- 📞 Canal USSD : +40%
- ⏰ Heures d'appels (8h-20h) : +20%
- 🔄 Type TRANSFERT/PAIEMENT : +10%

---

### 5️⃣ Vol Physique de Téléphone

**Description :** Retraits rapides après vol  
**Priorité :** 8/10  
**Critères de détection :**
- ⏰ Heure nocturne/soirée (18h-23h) : +30%
- 💰 Montant moyen (50k-300k) : +20%
- 🏪 RETRAIT via AGENT : +30%
- 📍 Zones à risque (Abobo, Adjamé, Yopougon) : +20%

---

### 6️⃣ Fraude par Agent Mobile Money

**Description :** Détournement par agent en fin de journée  
**Priorité :** 8/10  
**Critères de détection :**
- 🏪 Canal AGENT (obligatoire) : +30%
- ⏰ Fin de journée (18h-21h) : +30%
- 💰 Montant significatif (100k-500k) : +20%
- 🔄 Type DEPOT : +20%

---

### 7️⃣ Anomalie Comportementale

**Description :** Comportement suspect sans correspondance claire  
**Priorité :** 1/10 (Règle par défaut)  
**Score :** 30% constant

---

## Utilisation

### Intégration dans le Détecteur

Le classificateur est automatiquement intégré dans `detecteur.py` :

```python
from app.detector.classificateur_fraude import ClassificateurFraude

# Initialisation
classificateur = ClassificateurFraude()

# Classification
motif, description, confiance = classificateur.classifier(transaction, heure)
```

### Sortie Console Améliorée

```
🚨 ALERTE FRAUDE DÉTECTÉE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ Score de risque IA: -0.234
💰 Montant: 500 000 XOF
📍 Lieu: Abidjan-Yopougon à 3h
📱 Opérateur: Wave (Canal: APP)
🔄 Type: RETRAIT
👤 Expéditeur: 0712345678

🧐 Motif identifié: Broutage
   └─ Cybercriminalité: Transactions nocturnes massives via smartphone
   └─ Confiance: 90.0%
🛡️  MoneyShield CI - Alerte enregistrée en BDD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Base de Données

### Nouvelle Colonne : `confiance`

La table `alertes` inclut maintenant le score de confiance :

```sql
CREATE TABLE alertes (
    ...
    motif TEXT,
    confiance REAL DEFAULT 0.0
)
```

Cela permet de :
- Filtrer les alertes par niveau de confiance
- Améliorer les algorithmes en analysant les faux positifs
- Fournir des statistiques sur la qualité de détection

---

## Tests

Un script de test complet est disponible : [`test_classificateur.py`](file:///c:/Users/MARSHALL/Documents/Projets/mobile-money-ai/test_classificateur.py)

### Exécution

```bash
python test_classificateur.py
```

### Résultat Attendu

```
🛡️  MONEYSHIELD CI - Tests du Classificateur Intelligent

✅ Test Broutage:
   Motif: Broutage
   Confiance: 90.0%
   ✓ Test réussi!

✅ Test SIM Swap:
   Motif: SIM Swap
   Confiance: 95.0%
   ✓ Test réussi!

... (autres tests)

✅ TOUS LES TESTS ONT RÉUSSI!
```

---

## Avantages de cette Approche

### ✅ Plus Intelligent
- Scoring multi-critères au lieu de conditions arbitraires
- Prise en compte de plusieurs facteurs simultanément

### ✅ Plus Transparent
- Score de confiance explicite (0-100%)
- Description détaillée de chaque type de fraude

### ✅ Plus Maintenable
- Architecture orientée objet claire
- Facile d'ajouter de nouveaux types de fraudes

### ✅ Plus Évolutif
- Peut facilement être remplacé par un modèle ML multi-classe
- Support pour classification détaillée avec tous les scores

---

## Évolutions Futures Possibles

1. **Apprentissage automatique** : Remplacer les règles par un classificateur ML multi-classe entraîné sur les alertes validées

2. **Règles dynamiques** : Ajuster les poids des critères en fonction des retours terrain

3. **Détection combinée** : Détecter les fraudes qui combinent plusieurs techniques

4. **Scoring contextuel** : Ajuster les scores selon l'historique de l'utilisateur

---

## Questions Fréquentes

### Que se passe-t-il si plusieurs règles ont le même score ?

Le système utilise la **priorité** comme critère secondaire. Les fraudes les plus dangereuses (SIM Swap, Blanchiment) ont priorité 10.

### Peut-on personnaliser les seuils ?

Oui ! Il suffit de modifier les valeurs dans les méthodes `evaluer()` de chaque classe de règle.

### Comment ajouter un nouveau type de fraude ?

1. Créer une nouvelle classe héritant de `RegleFraude`
2. Implémenter la méthode `evaluer()`
3. Ajouter la règle dans `ClassificateurFraude.__init__()`

---

**Version :** 3.1  
**Date :** 2026-01-12  
**Auteur :** MoneyShield CI Team
