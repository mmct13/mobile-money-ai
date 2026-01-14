import time
import json
import random
import uuid
import os
from datetime import datetime
from kafka import KafkaProducer
from faker import Faker

# --- NOUVEAUX IMPORTS (Architecture Modulaire) ---
from app.config import KAFKA_TOPIC, MAP_VILLES, MAP_OPERATEURS

# --- CONFIGURATION ---
# Récupération dynamique de l'adresse (Docker ou Local)
KAFKA_SERVER = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')

# Initialisation de Faker
fake = Faker('fr_FR')

# Reconstruction des listes à partir de la config centrale
# (On prend les clés du dictionnaire pour avoir les noms)
VILLES_CI = list(MAP_VILLES.keys())
OPERATEURS = list(MAP_OPERATEURS.keys())

def init_kafka_producer():
    """Initialise le producteur Kafka."""
    print(f"[INFO] Connexion a Kafka sur : {KAFKA_SERVER} ...")
    try:
        producer = KafkaProducer(
            bootstrap_servers=[KAFKA_SERVER],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        print(f"[SUCCESS] Connecte avec succes a Kafka")
        return producer
    except Exception as e:
        print("\n" + "=" * 60)
        print("[ERROR] Connexion Kafka impossible")
        print(f"Details: {e}")
        print("\n[TIP] Verifiez que Kafka est demarre via Docker.")
        print("=" * 60 + "\n")
        return None


def generer_numero_ci(operateur_contexte=None):
    """
    Génère un numéro ivoirien valide (10 chiffres) selon l'opérateur.
    Règles :
    - Orange : commence par 07
    - MTN : commence par 05
    - Moov : commence par 01
    - Wave : Universel (peut être 07, 05 ou 01)
    - Inconnu/Autre : Aléatoire parmi les 3
    """
    prefixe = "01"  # Valeur par défaut

    # Choix du préfixe selon l'opérateur de la transaction
    if operateur_contexte == "Orange Money":
        prefixe = "07"
    elif operateur_contexte == "MTN MoMo":
        prefixe = "05"
    elif operateur_contexte == "Moov Money":
        prefixe = "01"
    else:
        # Cas Wave ou Destinataire (Hasard parmi les opérateurs CI)
        prefixe = random.choice(["07", "05", "01"])

    # Génération des 8 derniers chiffres
    suffixe = ''.join([str(random.randint(0, 9)) for _ in range(8)])

    return f"{prefixe}{suffixe}"


def generer_transaction():
    """Génère une transaction factice réaliste (v3.0)."""

    # Choix de l'opérateur pour cette transaction
    operateur_actuel = random.choice(OPERATEURS)
    
    # Choix du canal (Cohérent avec l'opérateur)
    if operateur_actuel == "Wave":
         # Wave est 99% App ou Carte
         canal = random.choice(["APP", "CARTE", "AGENT"])
    else:
         # Autres : USSD très fort
         canal = random.choice(["USSD", "APP", "AGENT"])

    # Simulation de la date et heure (Pas l'heure actuelle)
    # On reste sur la date d'aujourd'hui pour simplifier, mais on change l'heure
    maintenant = datetime.now()
    type_trans = random.choice(["RETRAIT", "DEPOT", "TRANSFERT"])
    
    # Logique cohérente avec entrainement.py
    if random.random() < 0.95:
        # CAS NORMAL : 06h00 - 22h00
        heure_simu = random.randint(6, 22)
        montant = random.randint(500, 50000)
        ville_trans = random.choice(VILLES_CI)
    else:
        # CAS SUSPECT (5%) : 10 Scénarios avancés
        scenario = random.choice([
            "BROUTAGE", "SOCIAL_ENG", "FAUX_NUMERO", "LOTERIE", 
            "FAUX_FRAIS", "SIM_SWAP", "BLANCHIMENT", "SOCIAL_MEDIA", 
            "FRAUDE_AGENT", "VOL_TEL"
        ])
        
        if scenario == "BROUTAGE":
            heure_simu = random.randint(0, 5)
            montant = random.randint(200000, 1000000)
            operateur_actuel = "Wave"
            canal = "APP"
            ville_trans = "Abidjan-Yopougon"
        elif scenario == "SIM_SWAP":
            heure_simu = random.randint(2, 6)
            montant = random.randint(500000, 2000000)
            canal = "AGENT"
            ville_trans = random.choice(VILLES_CI)
        elif scenario == "BLANCHIMENT":
            heure_simu = random.randint(8, 16)
            montant = random.randint(1500000, 5000000)
            canal = "AGENT"
            ville_trans = random.choice(["San-Pédro", "Soubré"])
        else:
            # Patterns génériques pour les autres types (Ingénierie sociale, etc)
            heure_simu = random.randint(0, 23)
            montant = random.randint(50000, 500000)
            ville_trans = random.choice(VILLES_CI)

    minute_simu = random.randint(0, 59)
    seconde_simu = random.randint(0, 59)
    
    date_simulee = maintenant.replace(hour=heure_simu, minute=minute_simu, second=seconde_simu, microsecond=0)

    # Génération des numéros en respectant la logique opérateur
    expediteur = generer_numero_ci(operateur_actuel)
    # Le destinataire peut être chez n'importe quel opérateur
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
    print("\n" + "=" * 60)
    print("MONEYSHIELD CI - Generateur de Transactions")
    print("=" * 60)
    
    producer = init_kafka_producer()
    if not producer:
        return

    print("\n[SUCCESS] GENERATEUR ACTIF")
    print("Simulation: Transactions Mobile Money CI")
    print("- Villes: 20 localites ivoiriennes")
    print("- Operateurs: Orange Money | MTN MoMo | Moov Money | Wave")
    print("\n[TIP] Appuyez sur CTRL+C pour arreter")
    print("-" * 60 + "\n")

    compteur = 0
    try:
        while True:
            # 1. Generer la donnee
            transaction = generer_transaction()

            # 2. Envoyer a Kafka
            producer.send(KAFKA_TOPIC, transaction)
            compteur += 1

            # Affichage console ameliore
            print(f"[INFO] #{compteur:04d} | {transaction['operateur']:15s} | {transaction['expediteur']} -> {transaction['montant']:>8,} F | {transaction['ville']}".replace(",", " "))

            # Pause aleatoire
            time.sleep(random.uniform(0.1, 2.0))

    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("[STOP] ARRET DU GENERATEUR")
        print(f"Total genere: {compteur} transactions")
        print("[INFO] Fermeture propre de Kafka...")
        producer.close()
        print("=" * 60 + "\n")


if __name__ == "__main__":
    main()