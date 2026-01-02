import json
import joblib
import pandas as pd
from kafka import KafkaConsumer
from datetime import datetime
import os
import time
# --- CONFIGURATION ---
DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
FICHIER_MODELE = os.path.join(DOSSIER_COURANT, "modele_fraude.pkl")

KAFKA_TOPIC = "flux_mobile_money"
KAFKA_BOOTSTRAP_SERVERS = ['127.0.0.1:9092']

# --- MAPPINGS (DOIT ETRE IDENTIQUE A ENTRAINEMENT.PY) ---
MAP_VILLES = {
    # Communes d'Abidjan (Détail)
    "Abidjan-Yopougon": 0, "Abidjan-Abobo": 1, "Abidjan-Cocody": 2,
    "Abidjan-Plateau": 3, "Abidjan-Marcory": 4, "Abidjan-Koumassi": 5, "Abidjan-Adjamé": 6,
    # Intérieur
    "Bouaké": 7, "Daloa": 8, "Yamoussoukro": 9, "San-Pédro": 10,
    "Korhogo": 11, "Man": 12, "Gagnoa": 13, "Grand-Bassam": 14,
    "Soubré": 15, "Aboisso": 16, "Odienné": 17, "Bondoukou": 18, "Séguéla": 19
}

MAP_TYPES = {
    "DEPOT": 0,
    "TRANSFERT": 1,
    "RETRAIT": 2,
    "PAIEMENT_MARCHAND": 3
}

MAP_OPERATEURS = {
    "Orange Money": 0,
    "MTN MoMo": 1,
    "Moov Money": 2,
    "Wave": 3
}

MAP_CANAUX = {
    "USSD": 0,
    "APP": 1,
    "CARTE": 2,
    "AGENT": 3
}


def charger_modele():
    """Charge le modèle IA de détection de fraude."""
    if not os.path.exists(FICHIER_MODELE):
        print("\n" + "=" * 60)
        print("❌ ERREUR: Modèle IA introuvable")
        print(f"📂 Chemin attendu: {FICHIER_MODELE}")
        print("\n💡 Solution:")
        print("   python app/detector/entrainement.py")
        print("=" * 60 + "\n")
        exit(1)
    print("\n" + "=" * 60)
    print("🛡️  MONEYSHIELD CI - Détecteur de Fraude IA")
    print("=" * 60)
    print("🧠 Chargement du modèle IA v3.0 (Granulaire)...")
    model = joblib.load(FICHIER_MODELE)
    print("✅ Modèle chargé avec succès")
    print("=" * 60 + "\n")
    return model



def main():
    model = charger_modele()

    # Initialisation Kafka
    try:
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            auto_offset_reset='latest',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ ERREUR: Connexion Kafka impossible")
        print(f"📋 Détails: {e}")
        print("\n💡 Vérifiez que Kafka est démarré:")
        print("   docker-compose up -d")
        print("=" * 60 + "\n")
        return

    print("🟢 SYSTÈME ACTIF - En écoute sur Kafka")
    print("📊 Analyse: Montant | Heure | Ville | Type | Opérateur | Canal")
    print("⏳ En attente de transactions...")
    print("\n" + "-" * 60 + "\n")

    for message in consumer:
        transaction = message.value

        try:
            # 1. Extraction et Transformation des données (Preprocessing)
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

            # 3. Prédiction
            prediction = model.predict(features)[0] 
            score = model.decision_function(features)[0]

            # 4. Logique d'affichage
            if prediction == -1:
                print("\n" + "━" * 60)
                print("🚨 ALERTE FRAUDE DÉTECTÉE")
                print("━" * 60)
                print(f"⚡ Score de risque: {score:.3f}")
                print(f"💰 Montant: {transaction['montant']:,.0f} XOF".replace(",", " "))
                print(f"📍 Lieu: {ville_str} à {heure}h")
                print(f"📱 Opérateur: {op_str} (Canal: {canal_str})")
                print(f"🔄 Type: {type_str}")
                print(f"👤 Expéditeur: {transaction['expediteur']}")
                # 4bis. Classification heuristique (MoneyShield CI)
                motif = "Inconnu"
                if transaction['montant'] > 1000000:
                    motif = "Blanchiment suspecté"
                elif heure < 6:
                    motif = "Broutage / Intrusion nocturne"
                elif transaction.get('canal') == "USSD":
                    motif = "Ingénierie Sociale / SIM Swap USSD"
                elif transaction.get('canal') == "APP" and transaction['montant'] > 200000:
                    motif = "Broutage App / Malware"
                elif transaction['ville'] in ["San-Pédro", "Soubré"] and transaction['montant'] > 500000:
                    motif = "Flux financier atypique (Zone Rurale)"
                else:
                    motif = "Anomalie comportementale IA"

                print(f"🧐 Motif probable: {motif}")
                print("🛡️  MoneyShield CI - Alerte enregistrée")
                print("━" * 60 + "\n")
                sauvegarder_alerte(transaction, score, heure, type_str, ville_str, motif)
            else:
                # Transaction normale
                print(f"✅ Transaction normale | {transaction['montant']:,} XOF | {op_str} ({canal_str}) | {ville_str}".replace(",", " "))

        except Exception as e:
            print(f"⚠️  Erreur de traitement: {e}")


def sauvegarder_alerte(transaction, score, heure, type_str, ville_str, motif):
    alerte = {
        "timestamp": time.time(),
        "date_heure": transaction['date_heure'],
        "montant": transaction['montant'],
        "expediteur": transaction['expediteur'],
        "ville": ville_str,
        "operateur": transaction['operateur'],
        "canal": transaction.get('canal', 'INCONNU'),
        "type": type_str,
        "score": score,
        "motif": motif
    }

    fichier_db = os.path.join(os.path.dirname(DOSSIER_COURANT), "dashboard", "alertes_db.json")

    data = []
    if os.path.exists(fichier_db):
        try:
            with open(fichier_db, 'r') as f:
                data = json.load(f)
        except:
            data = []

    data.append(alerte)

    with open(fichier_db, 'w') as f:
        json.dump(data, f, indent=4)



if __name__ == "__main__":
    main()