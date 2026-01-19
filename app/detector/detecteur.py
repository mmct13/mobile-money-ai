import json
import joblib
import pandas as pd
from kafka import KafkaConsumer
from datetime import datetime
import os
import time
from collections import deque

# --- NOUVEAUX IMPORTS (Architecture Modulaire) ---
from app.config import MAP_VILLES, MAP_TYPES, MAP_OPERATEURS, MAP_CANAUX, KAFKA_TOPIC
from app.database import get_connection
from app.detector.classificateur_fraude import ClassificateurFraude

# --- CONFIGURATION ---
DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
FICHIER_MODELE = os.path.join(DOSSIER_COURANT, "modele_fraude.pkl")

# Récupération de l'adresse Kafka (Docker ou Local)
# Si la variable d'env n'existe pas, on utilise localhost par défaut
KAFKA_SERVER = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')

def charger_modele():
    """Charge le modèle IA de détection de fraude."""
    if not os.path.exists(FICHIER_MODELE):
        print("\n" + "=" * 60)
        print("[ERROR] Modele IA introuvable")
        print(f"Chemin attendu: {FICHIER_MODELE}")
        print("\n[TIP] Solution:")
        print("   python -m app.detector.entrainement")
        print("=" * 60 + "\n")
        exit(1)
    
    print("\n" + "=" * 60)
    print("MONEYSHIELD CI - Detecteur de Fraude IA")
    print("=" * 60)
    print("[INFO] Chargement du modele IA v3.1 (Classification Intelligente)...")
    model = joblib.load(FICHIER_MODELE)
    print("[SUCCESS] Modele charge avec succes")
    print("=" * 60 + "\n")
    return model


def main():
    model = charger_modele()
    
    # Historique glissant pour détection temporelle (1000 dernières transactions)
    # Permet de détecter vélocité et schtroumpfage
    historique_transactions = deque(maxlen=1000)
    
    # Initialisation du classificateur intelligent
    classificateur = ClassificateurFraude()
    print("[INFO] Classificateur de fraude intelligent initialise")
    print("   - 9 types de fraudes detectables incluant:")
    print("      * Velocite Excessive (repetitions rapides)")
    print("      * Accumulation/Schtroumpfage (structuring)")
    print("      * Broutage, SIM Swap, Blanchiment...")
    print()

    # Initialisation Kafka
    print(f"[INFO] Connexion a Kafka sur : {KAFKA_SERVER} ...")
    try:
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=[KAFKA_SERVER],
            auto_offset_reset='latest',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
    except Exception as e:
        print("\n" + "=" * 60)
        print("[ERROR] Connexion Kafka impossible")
        print(f"Details: {e}")
        print("\n[TIP] Verifiez que Kafka est demarre via Docker.")
        print("=" * 60 + "\n")
        return

    print("[SUCCESS] SYSTEME ACTIF - En ecoute sur Kafka")
    print("ANALYSE: Montant | Heure | Ville | Type | Operateur | Canal")
    print("[INFO] En attente de transactions...")
    print("\n" + "-" * 60 + "\n")

    for message in consumer:
        transaction = message.value
        
        # Ajout à l'historique (au début pour accès rapide aux récents)
        # Note: Dans un système prod, Redis serait mieux, mais deque suffit ici
        historique_transactions.appendleft(transaction)

        try:
            # 1. Extraction et Transformation des données (Preprocessing)
            dt = datetime.fromisoformat(transaction['date_heure'])
            heure = dt.hour

            ville_str = transaction.get('ville')
            # Utilisation du mapping importé de app.config
            ville_code = MAP_VILLES.get(ville_str, -1)

            type_str = transaction.get('type_transaction')
            type_code = MAP_TYPES.get(type_str, -1)

            op_str = transaction.get('operateur')
            op_code = MAP_OPERATEURS.get(op_str, -1)
            
            canal_str = transaction.get('canal')
            canal_code = MAP_CANAUX.get(canal_str, -1)

            # 2. Création du vecteur pour l'IA
            features = pd.DataFrame([{
                "montant": transaction['montant'],
                "heure": heure,
                "ville_code": ville_code,
                "type_code": type_code,
                "operateur_code": op_code,
                "canal_code": canal_code
            }])

            # 3. Prédiction (Random Forest)
            # 0 = Normal, 1 = Fraude
            prediction = model.predict(features)[0] 
            
            # Probabilité de fraude (Classe 1)
            # predict_proba renvoie [[prob_0, prob_1]]
            proba_fraude = model.predict_proba(features)[0][1]
            
            # --- CONTEXTE POUR CLASSIFICATION ---
            contexte = {
                'heure': heure,
                'historique': list(historique_transactions)
            }

            # 4. Logique d'affichage
            if prediction == 1:
                print("\n" + "━" * 60)
                print("[ALERT] FRAUDE DETECTEE")
                print("━" * 60)
                print(f" - Probabilite Fraude: {proba_fraude*100:.1f}%")
                print(f" - Montant: {transaction['montant']:,.0f} XOF".replace(",", " "))
                print(f" - Lieu: {ville_str} a {heure}h")
                print(f" - Operateur: {op_str} (Canal: {canal_str})")
                print(f" - Type: {type_str}")
                print(f" - Expediteur: {transaction['expediteur']}")
                
                # 4bis. Classification intelligente avec CONTEXTE
                motif, description, confiance_regles = classificateur.classifier(transaction, contexte)
                
                # On combine la confiance IA et Règles
                # Si l'IA est très sûre, ça renforce
                confiance_globale = (proba_fraude + confiance_regles) / 2
                
                print(f" - Motif identifie: {motif}")
                print(f"   Details: {description}")
                print(f"   Confiance Globale: {confiance_globale*100:.1f}%")
                print("[INFO] Alerte enregistree en BDD")
                print("━" * 60 + "\n")
                
                # APPEL DE LA NOUVELLE FONCTION DE SAUVEGARDE SQL
                # On passe proba_fraude comme score
                sauvegarder_alerte(transaction, proba_fraude, type_str, ville_str, motif, confiance_globale)
            else:
                # Transaction normale
                print(f"[INFO] Transaction normale | {transaction['montant']:,} XOF | {op_str} ({canal_str}) | {ville_str}".replace(",", " "))

        except Exception as e:
            print(f"[ERROR] Erreur de traitement: {e}")
        
        # 5. Sauvegarde SYSTÉMATIQUE de toutes les transactions pour le Dashboard Financier
        try:
            sauvegarder_transaction(transaction)
        except Exception as e:
             # On ne veut pas bloquer le procesus pour ça
            pass



def sauvegarder_alerte(transaction, score, type_str, ville_str, motif, confiance):
    """Sauvegarde l'alerte dans SQLite avec le score de confiance."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Requête SQL sécurisée avec confiance
        sql = '''
            INSERT INTO alertes 
            (timestamp, date_heure, montant, expediteur, ville, operateur, canal, type_trans, score, motif, confiance)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        valeurs = (
            time.time(),
            transaction['date_heure'],
            transaction['montant'],
            transaction['expediteur'],
            ville_str,
            transaction['operateur'],
            transaction.get('canal', 'INCONNU'),
            type_str,
            float(score),
            motif,
            float(confiance)
        )
        
        cursor.execute(sql, valeurs)
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"⚠️ Erreur lors de l'écriture en base de données: {e}")


def sauvegarder_transaction(transaction):
    """Sauvegarde toutes les transactions pour le dashboard financier."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        sql = '''
            INSERT INTO transactions 
            (transaction_id, timestamp, date_heure, montant, expediteur, destinataire, ville, operateur, canal, type_trans)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        valeurs = (
            transaction.get('transaction_id', 'N/A'),
            time.time(),
            transaction['date_heure'],
            transaction['montant'],
            transaction.get('expediteur', 'N/A'),
            transaction.get('destinataire', 'N/A'),
            transaction.get('ville', 'N/A'),
            transaction['operateur'],
            transaction.get('canal', 'INCONNU'),
            transaction.get('type_transaction', 'N/A')
        )
        
        cursor.execute(sql, valeurs)
        conn.commit()
        conn.close()
        
    except Exception as e:
        # En prod, logger silencieusement ou dans un fichier de log
        print(f"[DB ERROR] Save Transaction: {e}")


if __name__ == "__main__":
    main()