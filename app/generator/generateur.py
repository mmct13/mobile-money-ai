import time
import json
import random
import uuid
import os
import logging
from datetime import datetime
from kafka import KafkaProducer
from faker import Faker
from typing import Dict, Optional

# --- NOUVEAUX IMPORTS (Architecture Modulaire) ---
from app.config import KAFKA_TOPIC, MAP_VILLES, MAP_OPERATEURS

# --- CONFIGURATION LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
KAFKA_SERVER = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')

fake = Faker('fr_FR')

VILLES_CI = list(MAP_VILLES.keys())
OPERATEURS = list(MAP_OPERATEURS.keys())

def init_kafka_producer() -> Optional[KafkaProducer]:
    """Initialise le producteur Kafka."""
    logger.info(f"Connexion a Kafka sur : {KAFKA_SERVER} ...")
    try:
        producer = KafkaProducer(
            bootstrap_servers=[KAFKA_SERVER],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        logger.info("Connecte avec succes a Kafka")
        return producer
    except Exception as e:
        logger.error("Connexion Kafka impossible")
        logger.error(f"Details: {e}")
        logger.info("Verifiez que Kafka est demarre via Docker.")
        return None


def generer_numero_ci(operateur_contexte: Optional[str] = None) -> str:
    """
    Génère un numéro ivoirien valide (10 chiffres) selon l'opérateur.
    """
    prefixe = "01"

    if operateur_contexte == "Orange Money":
        prefixe = "07"
    elif operateur_contexte == "MTN MoMo":
        prefixe = "05"
    elif operateur_contexte == "Moov Money":
        prefixe = "01"
    else:
        prefixe = random.choice(["07", "05", "01"])

    suffixe = ''.join([str(random.randint(0, 9)) for _ in range(8)])

    return f"{prefixe}{suffixe}"


def generer_transaction() -> Dict:
    """Génère une transaction factice réaliste (v3.0)."""

    operateur_actuel = random.choice(OPERATEURS)
    
    if operateur_actuel == "Wave":
         canal = random.choice(["APP", "CARTE", "AGENT"])
    else:
         canal = random.choice(["USSD", "APP", "AGENT"])

    maintenant = datetime.now()
    type_trans = random.choice(["RETRAIT", "DEPOT", "TRANSFERT"])
    
    # --- LOGIQUE METIER (Montants & Types) ---
    if random.random() < 0.95:
        # CAS NORMAL
        montant = random.randint(500, 50000)
        ville_trans = random.choice(VILLES_CI)
    else:
        # CAS SUSPECT (5%)
        scenario = random.choice([
            "BROUTAGE", "SOCIAL_ENG", "FAUX_NUMERO", "LOTERIE", 
            "FAUX_FRAIS", "SIM_SWAP", "BLANCHIMENT", "SOCIAL_MEDIA", 
            "FRAUDE_AGENT", "VOL_TEL"
        ])
        
        if scenario == "BROUTAGE":
            montant = random.randint(200000, 1000000)
            operateur_actuel = "Wave"
            canal = "APP"
            ville_trans = "Abidjan-Yopougon"
        elif scenario == "SIM_SWAP":
            montant = random.randint(500000, 2000000)
            canal = "AGENT"
            ville_trans = random.choice(VILLES_CI)
        elif scenario == "BLANCHIMENT":
            montant = random.randint(1500000, 5000000)
            canal = "AGENT"
            ville_trans = random.choice(["San-Pédro", "Soubré"])
        else:
            montant = random.randint(50000, 500000)
            ville_trans = random.choice(VILLES_CI)

    # --- MODIFICATION TEMPS REEL ---
    # On utilise l'heure actuelle du système pour que le tableau de bord soit en temps réel
    date_simulee = maintenant

    expediteur = generer_numero_ci(operateur_actuel)
    destinataire = generer_numero_ci(None)

    transaction = {
        "transaction_id": str(uuid.uuid4()),
        "date_heure": date_simulee.isoformat(),
        "expediteur": expediteur,
        "destinataire": destinataire,
        "montant": montant,
        "devise": "XOF",
        "operateur": operateur_actuel,
        "canal": canal,
        "ville": ville_trans,
        "type_transaction": type_trans
    }
    return transaction


def main():
    logger.info("=" * 60)
    logger.info("MONEYSHIELD CI - Generateur de Transactions")
    logger.info("=" * 60)
    
    producer = init_kafka_producer()
    if not producer:
        return

    logger.info("GENERATEUR ACTIF")
    logger.info("- Villes: 20 localites ivoiriennes")
    logger.info("- Operateurs: Orange Money | MTN MoMo | Moov Money | Wave")

    compteur = 0
    try:
        while True:
            # 1. Generer la donnee
            transaction = generer_transaction()

            # 2. Envoyer a Kafka
            producer.send(KAFKA_TOPIC, transaction)
            compteur += 1

            # Affichage console
            logger.info(f"#{compteur:04d} | {transaction['operateur']:15s} | {transaction['expediteur']} -> {transaction['montant']:>8,} F | {transaction['ville']}".replace(",", " "))

            # Pause aleatoire
            time.sleep(random.uniform(0.1, 2.0))

    except KeyboardInterrupt:
        logger.info("ARRET DU GENERATEUR")
        logger.info(f"Total genere: {compteur} transactions")
        producer.close()


if __name__ == "__main__":
    main()