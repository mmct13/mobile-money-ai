# 🗂️ Visualisation de la Base de Données MoneyShield CI

## 📋 Méthodes pour Visualiser les Tables

### **Méthode 1 : Script Interactif (Recommandé)**

J'ai créé un script Python interactif `view_database.py` avec un menu complet.

**Utilisation :**
```bash
# Option 1 : Via le script batch
.\view_database.bat

# Option 2 : Directement avec Python
.\.venv\Scripts\python.exe view_database.py
```

**Fonctionnalités disponibles :**
1. 📋 Afficher toutes les tables
2. 📊 Afficher le schéma de la table 'alertes'
3. 🔢 Compter les alertes
4. 🚨 Afficher les dernières alertes
5. 📊 Afficher les statistiques complètes
6. 💰 Rechercher des alertes par montant
7. 📍 Afficher les alertes par ville
8. 📱 Afficher les alertes par opérateur

---

### **Méthode 2 : Ligne de Commande Python**

**Voir le nombre d'alertes :**
```bash
.\.venv\Scripts\python.exe -c "import sqlite3; conn = sqlite3.connect('moneyshield.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM alertes'); print(f'Alertes: {cursor.fetchone()[0]}'); conn.close()"
```

**Afficher les 10 dernières alertes :**
```bash
.\.venv\Scripts\python.exe -c "import sqlite3; conn = sqlite3.connect('moneyshield.db'); cursor = conn.cursor(); cursor.execute('SELECT * FROM alertes ORDER BY id DESC LIMIT 10'); print(*cursor.fetchall(), sep='\n'); conn.close()"
```

---

### **Méthode 3 : Outils SQLite Externes**

#### **DB Browser for SQLite (Gratuit)**
1. Télécharger : https://sqlitebrowser.org/dl/
2. Installer l'application
3. Ouvrir le fichier `moneyshield.db`
4. Interface graphique complète pour explorer les tables

#### **VSCode Extension**
1. Installer l'extension "SQLite Viewer" ou "SQLite" dans VSCode
2. Ouvrir `moneyshield.db` dans VSCode
3. Clic droit → "Open Database"

#### **DBeaver (Gratuit)**
1. Télécharger : https://dbeaver.io/download/
2. Créer une connexion SQLite
3. Pointer vers `moneyshield.db`

---

### **Méthode 4 : Commandes SQLite Directes**

Si vous avez `sqlite3` installé :
```bash
# Ouvrir la base de données
sqlite3 moneyshield.db

# Commandes SQLite
.tables                          # Lister les tables
.schema alertes                  # Voir le schéma
SELECT COUNT(*) FROM alertes;    # Compter
SELECT * FROM alertes LIMIT 10;  # Voir les données
.quit                            # Quitter
```

---

### **Méthode 5 : Dashboard Streamlit**

Le dashboard sur `http://localhost:8501` affiche déjà les données en temps réel avec des graphiques !

---

## 📊 Structure de la Table `alertes`

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | INTEGER | Identifiant unique (auto-incrémenté) |
| `timestamp` | REAL | Timestamp Unix de la détection |
| `date_heure` | TEXT | Date et heure ISO de la transaction |
| `montant` | INTEGER | Montant de la transaction (XOF) |
| `expediteur` | TEXT | Numéro de téléphone de l'expéditeur |
| `ville` | TEXT | Ville de la transaction |
| `operateur` | TEXT | Opérateur mobile money |
| `canal` | TEXT | Canal utilisé (USSD, APP, CARTE, AGENT) |
| `type_trans` | TEXT | Type de transaction |
| `score` | REAL | Score de risque IA |
| `motif` | TEXT | Motif de l'alerte |

---

## 🔍 Exemples de Requêtes SQL Utiles

```sql
-- Top 10 des alertes par montant
SELECT montant, ville, operateur, motif 
FROM alertes 
ORDER BY montant DESC 
LIMIT 10;

-- Statistiques par opérateur
SELECT operateur, COUNT(*) as nb, AVG(montant) as montant_moyen
FROM alertes
GROUP BY operateur
ORDER BY nb DESC;

-- Alertes par ville
SELECT ville, COUNT(*) as nb
FROM alertes
GROUP BY ville
ORDER BY nb DESC;

-- Alertes par motif
SELECT motif, COUNT(*) as nb
FROM alertes
GROUP BY motif
ORDER BY nb DESC;

-- Alertes de la dernière heure
SELECT *
FROM alertes
WHERE datetime(date_heure) > datetime('now', '-1 hour')
ORDER BY id DESC;

-- Montants suspects (> 1 000 000 F)
SELECT *
FROM alertes
WHERE montant > 1000000
ORDER BY montant DESC;
```

---

## 🎯 Recommandation

**Pour une exploration rapide :** Utilisez `view_database.bat`  
**Pour une analyse approfondie :** Utilisez DB Browser for SQLite  
**Pour le monitoring en temps réel :** Utilisez le dashboard Streamlit
