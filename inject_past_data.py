import json
import uuid
import time
import random
import os
from datetime import datetime, timedelta
from kafka import KafkaProducer
from app.config import KAFKA_TOPIC, MAP_VILLES, MAP_OPERATEURS

# --- CONFIGURATION ---
KAFKA_SERVER = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')

VILLES_CI = list(MAP_VILLES.keys())
OPERATEURS = list(MAP_OPERATEURS.keys())

def init_kafka_producer():
    try:
        producer = KafkaProducer(
            bootstrap_servers=[KAFKA_SERVER],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        return producer
    except Exception as e:
        print(f"[ERREUR] Connexion Kafka impossible: {e}")
        return None

def generer_numero_ci(operateur_contexte=None):
    prefixe = "01"
    if operateur_contexte == "Orange Money": prefixe = "07"
    elif operateur_contexte == "MTN MoMo": prefixe = "05"
    elif operateur_contexte == "Moov Money": prefixe = "01"
    else: prefixe = random.choice(["07", "05", "01"])
    suffixe = ''.join([str(random.randint(0, 9)) for _ in range(8)])
    return f"{prefixe}{suffixe}"

def injecter_donnees_passees():
    producer = init_kafka_producer()
    if not producer:
        return

    print("=" * 60)
    print("INJECTION D'HISTORIQUE (J-3 a J-1)")
    print("=" * 60)
    print("Génération de transactions datant de 2 à 3 jours en arrière...")

    maintenant = datetime.now()
    # On commence il y a 3 jours (72h) et on s'arrête il y a 1 jour (24h)
    start_date = maintenant - timedelta(days=3)
    end_date = maintenant - timedelta(days=1)
    
    total_envoye = 0
    
    # On parcourt heure par heure
    current_time = start_date
    while current_time < end_date:
        # Nombre de transactions variable selon l'heure
        heure = current_time.hour
        if 0 <= heure < 6:
            nb_trans = random.randint(2, 8)
        elif 6 <= heure < 12:
            nb_trans = random.randint(15, 30)
        elif 12 <= heure < 18:
            nb_trans = random.randint(20, 45)
        else:
            nb_trans = random.randint(10, 25)
            
        for _ in range(nb_trans):
            # Décalage aléatoire dans l'heure
            minute = random.randint(0, 59)
            trans_date = current_time.replace(minute=minute, second=random.randint(0, 59))
            
            # Logique transaction
            operateur = random.choice(OPERATEURS)
            if operateur == "Wave": canal = random.choice(["APP", "CARTE", "AGENT"])
            else: canal = random.choice(["USSD", "APP", "AGENT"])
            
            montant = random.randint(500, 75000)
            ville = random.choice(VILLES_CI)
            type_trans = random.choice(["RETRAIT", "DEPOT", "TRANSFERT"])
            
            transaction = {
                "transaction_id": str(uuid.uuid4()),
                "date_heure": trans_date.isoformat(),
                "expediteur": generer_numero_ci(operateur),
                "destinataire": generer_numero_ci(None),
                "montant": montant,
                "devise": "XOF",
                "operateur": operateur,
                "canal": canal,
                "ville": ville,
                "type_transaction": type_trans
            }
            
            producer.send(KAFKA_TOPIC, transaction)
            total_envoye += 1
        
        current_time += timedelta(hours=1)
        print(f"Injection: {current_time.strftime('%Y-%m-%d %H:00')} - {nb_trans} TXs envoyées.")

    producer.flush()
    print("=" * 60)
    print(f"TERMINÉ. Total injecté: {total_envoye} transactions.")
    print("Période couverte : {} à {}".format(start_date.strftime('%Y-%m-%d %H:%M'), end_date.strftime('%Y-%m-%d %H:%M')))
    print("=" * 60)

if __name__ == "__main__":
    injecter_donnees_passees()
