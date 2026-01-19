import json
import uuid
import time
import os
from datetime import datetime
from kafka import KafkaProducer
from app.config import KAFKA_TOPIC

# --- CONFIGURATION ---
KAFKA_SERVER = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')

def init_kafka_producer():
    """Initialise le producteur Kafka."""
    try:
        producer = KafkaProducer(
            bootstrap_servers=[KAFKA_SERVER],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        return producer
    except Exception as e:
        print(f"[ERREUR] Impossible de se connecter a Kafka ({KAFKA_SERVER})")
        print(f"Details: {e}")
        return None

def inject_scenario():
    producer = init_kafka_producer()
    if not producer:
        return

    # --- CONSTRUCTION DU SCENARIO ---
    # Action : Un retrait massif de 2.000.000 FCFA.
    # Lieu : Korhogo (Zone Nord), alors que l'abonné réside habituellement à Abidjan.
    # Heure : 03h00 du matin (Heure de faible affluence).
    
    # On force l'heure à 03:00 aujourd'hui
    maintenant = datetime.now()
    date_simulee = maintenant.replace(hour=3, minute=0, second=0, microsecond=0)

    # Payload JSON
    transaction = {
        "transaction_id": str(uuid.uuid4()),
        "date_heure": date_simulee.isoformat(),
        "expediteur": "0799887766", # Numéro Orange
        "destinataire": "0123456789",
        "montant": 2000000,
        "devise": "XOF",
        "operateur": "Orange Money",
        "canal": "AGENT", # Retrait massif souvent en cash point
        "ville": "Korhogo",
        "type_transaction": "RETRAIT"
    }

    print("\n" + "="*60)
    print("INJECTION DE SCENARIO : RETRAIT SUSPECT KORHOGO")
    print("="*60)
    print(f"Time (T0)      : {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
    print(f"Montant        : {transaction['montant']:,} FCFA")
    print(f"Ville          : {transaction['ville']}")
    print(f"Heure Simulee  : {transaction['date_heure']}")
    print("-" * 60)

    # Envoi Kafka
    future = producer.send(KAFKA_TOPIC, transaction)
    producer.flush()
    
    # Attente de la confirmation Kafka
    record_metadata = future.get(timeout=10)
    
    print(f"Status Kafka   : SUCCES")
    print(f"Topic          : {record_metadata.topic}")
    print(f"Partition      : {record_metadata.partition}")
    print(f"Offset         : {record_metadata.offset}")
    print("="*60 + "\n")

if __name__ == "__main__":
    inject_scenario()
