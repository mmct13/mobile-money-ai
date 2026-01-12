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
        print("❌ ERREUR: Modèle IA introuvable")
        print(f"📂 Chemin attendu: {FICHIER_MODELE}")
        print("\n💡 Solution:")
        print("   python -m app.detector.entrainement")
        print("=" * 60 + "\n")
        exit(1)
    
    print("\n" + "=" * 60)
    print("🛡️  MONEYSHIELD CI - Détecteur de Fraude IA")
    print("=" * 60)
    print("🧠 Chargement du modèle IA v3.1 (Classification Intelligente)...")
    model = joblib.load(FICHIER_MODELE)
    print("✅ Modèle chargé avec succès")
    print("=" * 60 + "\n")
    return model


def main():
    model = charger_modele()
    
    # Historique glissant pour détection temporelle (1000 dernières transactions)
    # Permet de détecter vélocité et schtroumpfage
    historique_transactions = deque(maxlen=1000)
    
    # Initialisation du classificateur intelligent
    classificateur = ClassificateurFraude()
    print("🎯 Classificateur de fraude intelligent initialisé")
    print("   📋 9 types de fraudes détectables incluant:")
    print("      • Vélocité Excessive (répétitions rapides)")
    print("      • Accumulation/Schtroumpfage (structuring)")
    print("      • Broutage, SIM Swap, Blanchiment...")
    print()

    # Initialisation Kafka
    print(f"⏳ Connexion à Kafka sur : {KAFKA_SERVER} ...")
    try:
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=[KAFKA_SERVER],
            auto_offset_reset='latest',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ ERREUR: Connexion Kafka impossible")
        print(f"📋 Détails: {e}")
        print("\n💡 Vérifiez que Kafka est démarré via Docker.")
        print("=" * 60 + "\n")
        return

    print("🟢 SYSTÈME ACTIF - En écoute sur Kafka")
    print("📊 Analyse: Montant | Heure | Ville | Type | Opérateur | Canal")
    print("⏳ En attente de transactions...")
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

            # 3. Prédiction
            prediction = model.predict(features)[0] 
            score = model.decision_function(features)[0]
            
            # --- CONTEXTE POUR CLASSIFICATION ---
            contexte = {
                'heure': heure,
                'historique': list(historique_transactions)
            }

            # 4. Logique d'affichage
            if prediction == -1:
                print("\n" + "━" * 60)
                print("🚨 ALERTE FRAUDE DÉTECTÉE")
                print("━" * 60)
                print(f"⚡ Score de risque IA: {score:.3f}")
                print(f"💰 Montant: {transaction['montant']:,.0f} XOF".replace(",", " "))
                print(f"📍 Lieu: {ville_str} à {heure}h")
                print(f"📱 Opérateur: {op_str} (Canal: {canal_str})")
                print(f"🔄 Type: {type_str}")
                print(f"👤 Expéditeur: {transaction['expediteur']}")
                
                # 4bis. Classification intelligente avec CONTEXTE
                motif, description, confiance = classificateur.classifier(transaction, contexte)
                
                print(f"🧐 Motif identifié: {motif}")
                print(f"   └─ {description}")
                print(f"   └─ Confiance: {confiance*100:.1f}%")
                print("🛡️  MoneyShield CI - Alerte enregistrée en BDD")
                print("━" * 60 + "\n")
                
                # APPEL DE LA NOUVELLE FONCTION DE SAUVEGARDE SQL
                sauvegarder_alerte(transaction, score, type_str, ville_str, motif, confiance)
            else:
                # Transaction normale
                print(f"✅ Transaction normale | {transaction['montant']:,} XOF | {op_str} ({canal_str}) | {ville_str}".replace(",", " "))

        except Exception as e:
            print(f"⚠️  Erreur de traitement: {e}")



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


if __name__ == "__main__":
    main()