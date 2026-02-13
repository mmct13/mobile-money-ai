import json
import joblib
import pandas as pd
from kafka import KafkaConsumer
from datetime import datetime
import os
import time
import logging
from collections import deque
from typing import Dict, Any, Optional

# --- NOUVEAUX IMPORTS (Architecture Modulaire) ---
from app.config import MAP_VILLES, MAP_TYPES, MAP_OPERATEURS, MAP_CANAUX, KAFKA_TOPIC
from app.database import get_connection
from app.detector.classificateur_fraude import ClassificateurFraude

# --- CONFIGURATION LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
FICHIER_MODELE = os.path.join(DOSSIER_COURANT, "modele_fraude.pkl")

# Récupération de l'adresse Kafka (Docker ou Local)
KAFKA_SERVER = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')

def charger_modele() -> Any:
    """Charge le modèle IA de détection de fraude."""
    if not os.path.exists(FICHIER_MODELE):
        logger.error("Modèle IA introuvable")
        logger.error(f"Chemin attendu: {FICHIER_MODELE}")
        logger.info("Solution: python -m app.detector.entrainement")
        exit(1)
    
    logger.info("=" * 60)
    logger.info("MONEYSHIELD CI - Detecteur de Fraude IA")
    logger.info("=" * 60)
    logger.info("Chargement du modele IA v3.1 (Classification Intelligente)...")
    try:
        model = joblib.load(FICHIER_MODELE)
        logger.info("Modele charge avec succes")
        return model
    except Exception as e:
        logger.critical(f"Erreur fatale lors du chargement du modèle: {e}")
        exit(1)


def main():
    model = charger_modele()
    
    # Historique glissant pour détection temporelle (1000 dernières transactions)
    historique_transactions = deque(maxlen=1000)
    
    # Initialisation du classificateur intelligent
    classificateur = ClassificateurFraude()
    logger.info("Classificateur de fraude intelligent initialise")
    
    # Initialisation Kafka
    logger.info(f"Connexion a Kafka sur : {KAFKA_SERVER} ...")
    try:
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=[KAFKA_SERVER],
            auto_offset_reset='latest',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
    except Exception as e:
        logger.error("Connexion Kafka impossible")
        logger.error(f"Details: {e}")
        logger.info("Verifiez que Kafka est demarre via Docker.")
        return

    logger.info("SYSTEME ACTIF - En ecoute sur Kafka")
    logger.info("En attente de transactions...")
    
    for message in consumer:
        transaction = message.value
        
        # Ajout à l'historique
        historique_transactions.appendleft(transaction)

        try:
            # 1. Extraction et Transformation des données
            dt = datetime.fromisoformat(transaction['date_heure'])
            heure = dt.hour

            ville_str = transaction.get('ville')
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
            prediction = model.predict(features)[0] 
            proba_fraude = model.predict_proba(features)[0][1]
            
            # --- CONTEXTE POUR CLASSIFICATION ---
            contexte = {
                'heure': heure,
                'historique': list(historique_transactions)
            }

            # 4. Logique d'affichage
            if prediction == 1:
                logger.warning("FRAUDE DETECTEE")
                logger.warning(f"Probabilite: {proba_fraude*100:.1f}% | Montant: {transaction['montant']:,.0f} XOF".replace(",", " "))
                logger.warning(f"Lieu: {ville_str} | Op: {op_str}")

                # 4bis. Classification intelligente avec CONTEXTE
                motif, description, confiance_regles = classificateur.classifier(transaction, contexte)
                
                confiance_globale = (proba_fraude + confiance_regles) / 2
                
                logger.warning(f"Motif: {motif} | Confiance Globale: {confiance_globale*100:.1f}%")
                
                sauvegarder_alerte(transaction, proba_fraude, type_str, ville_str, motif, confiance_globale)
            else:
                # Transaction normale
                logger.info(f"OK | {transaction['montant']:,} F | {op_str} | {ville_str}".replace(",", " "))

        except Exception as e:
            logger.error(f"Erreur de traitement: {e}")
        
        # 5. Sauvegarde SYSTÉMATIQUE
        try:
            sauvegarder_transaction(transaction)
        except Exception as e:
             pass


def sauvegarder_alerte(transaction: Dict, score: float, type_str: str, ville_str: str, motif: str, confiance: float):
    """Sauvegarde l'alerte dans SQLite avec le score de confiance."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
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
        logger.error(f"Erreur lors de l'écriture Alerte BDD: {e}")


def sauvegarder_transaction(transaction: Dict):
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
        pass # Silence en prod pour perf, ou logger.debug


if __name__ == "__main__":
    main()