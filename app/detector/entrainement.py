import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import joblib
import random
from faker import Faker
import os
from app.config import MAP_VILLES, MAP_TYPES, MAP_OPERATEURS, MAP_CANAUX

# --- CONFIGURATION ---
DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
FICHIER_MODELE = os.path.join(DOSSIER_COURANT, "modele_fraude.pkl")
NB_TRANSACTIONS = 50000  # Encore plus de données pour la précision

fake = Faker('fr_FR')

def generer_donnees_historiques():
    """Génère des données avec contexte enrichi (Communes, Canaux)."""
    data = []

    for _ in range(NB_TRANSACTIONS):
        # Initialisation par défaut
        ville = random.choice(list(MAP_VILLES.keys()))
        operateur = random.choice(list(MAP_OPERATEURS.keys()))
        type_trans = random.choice(list(MAP_TYPES.keys()))
        
        # Logique Canal (Cohérence)
        if operateur == "Wave":
            canal = random.choice(["APP", "CARTE", "AGENT"])
        else:
            # Orange/MTN/Moov : Beaucoup d'USSD
            canal = random.choice(["USSD", "APP", "AGENT"])

        # 96% de transactions normales
        if random.random() < 0.96:
            montant = random.randint(500, 75000)
            heure = random.randint(6, 22)
            
            # Ajustement Canal Normal
            if type_trans == "DEPOT" or type_trans == "RETRAIT":
                 canal = "AGENT" # En général fait en kiosque

        else:
            # 4% d'anomalies (Scénarios Avancés MoneyShield CI)
            scenario = random.choice([
                "BROUTAGE", "SOCIAL_ENG", "FAUX_NUMERO", "LOTERIE", 
                "FAUX_FRAIS", "SIM_SWAP", "BLANCHIMENT", "SOCIAL_MEDIA", 
                "FRAUDE_AGENT", "VOL_TEL"
            ])
            
            if scenario == "BROUTAGE": # Cybercriminalité standard
                montant = random.randint(200000, 1000000)
                heure = random.randint(0, 5) # Nuit
                ville = "Abidjan-Yopougon"
                type_trans = "RETRAIT"
                operateur = "Wave"
                canal = "APP"

            elif scenario == "SOCIAL_ENG": # Phishing/Vishing
                montant = random.randint(50000, 200000)
                heure = random.randint(8, 18)
                type_trans = "TRANSFERT"
                canal = "USSD"
                
            elif scenario == "FAUX_NUMERO": # Arnaque au mauvais numéro
                montant = random.randint(10000, 50000)
                heure = random.randint(12, 20)
                type_trans = "TRANSFERT"
                canal = "USSD"

            elif scenario == "LOTERIE": # Faux gains
                montant = random.randint(100000, 500000)
                heure = random.randint(9, 17)
                type_trans = "TRANSFERT"
                canal = "APP"

            elif scenario == "FAUX_FRAIS": # Douane/Livraison
                montant = random.randint(20000, 150000)
                heure = random.randint(10, 16)
                type_trans = "PAIEMENT_MARCHAND"
                canal = "APP"

            elif scenario == "SIM_SWAP": # Vol d'identité
                montant = random.randint(500000, 2000000)
                heure = random.randint(2, 6) # Tôt le matin
                type_trans = "RETRAIT"
                canal = "AGENT"

            elif scenario == "BLANCHIMENT": # Mules financières
                montant = random.randint(1500000, 5000000)
                heure = random.randint(8, 16)
                ville = random.choice(["San-Pédro", "Soubré"])
                type_trans = "DEPOT"
                canal = "AGENT"

            elif scenario == "SOCIAL_MEDIA": # WhatsApp/FB Scam
                montant = random.randint(5000, 100000)
                heure = random.randint(18, 23)
                type_trans = "TRANSFERT"
                canal = "APP"

            elif scenario == "FRAUDE_AGENT": # Détournement agent
                montant = random.randint(100000, 300000)
                heure = random.randint(18, 20) # Fin de journée
                type_trans = "DEPOT"
                canal = "AGENT"

            elif scenario == "VOL_TEL": # Vol physique
                montant = random.randint(50000, 300000)
                heure = random.randint(20, 23)
                ville = random.choice(["Abidjan-Abobo", "Abidjan-Adjamé"])
                type_trans = "RETRAIT"
                canal = "AGENT"

        data.append({
            "montant": montant,
            "ville": ville,
            "type": type_trans,
            "heure": heure,
            "operateur": operateur,
            "canal": canal
        })

    return pd.DataFrame(data)


def preparer_features(df):
    """Transforme tout en numérique."""
    df_encoded = df.copy()

    df_encoded['ville_code'] = df_encoded['ville'].map(MAP_VILLES)
    df_encoded['type_code'] = df_encoded['type'].map(MAP_TYPES)
    df_encoded['operateur_code'] = df_encoded['operateur'].map(MAP_OPERATEURS)
    df_encoded['canal_code'] = df_encoded['canal'].map(MAP_CANAUX)

    # 6 Features maintenant (+ Canal)
    return df_encoded[["montant", "heure", "ville_code", "type_code", "operateur_code", "canal_code"]]


def main():
    print("\n" + "=" * 60)
    print("[INFO] MONEYSHIELD CI - Entrainement du Modele IA")
    print("=" * 60)
    print("\n[INFO] Phase 1: Generation du dataset")
    print("   - Villes: 20 localites ivoiriennes (Abidjan detaille)")
    print("   - Canaux: USSD | APP | CARTE | AGENT")
    print("   - Scenarios de fraude: 5 types (Brouteur, Blanchiment...)")
    print(f"   - Volume: {NB_TRANSACTIONS:,} transactions".replace(",", " "))
    print("\n[INFO] Generation en cours...")
    df = generer_donnees_historiques()
    print(f"[SUCCESS] Dataset genere: {len(df):,} transactions".replace(",", " "))

    print("\n[INFO] Phase 2: Entrainement du modele")
    print("   - Algorithme: Isolation Forest")
    print("   - Features: 6 dimensions (Montant, Heure, Ville, Type, Operateur, Canal)")
    print("   - Contamination: 4%")
    print("   - Estimateurs: 250 arbres")
    print("\n[INFO] Entrainement en cours...")
    X = preparer_features(df)

    model = IsolationForest(n_estimators=250, contamination=0.04, random_state=42, n_jobs=-1)
    model.fit(X)
    print("[SUCCESS] Modele entraine avec succes")

    print("\n[INFO] Phase 3: Sauvegarde du modele")
    joblib.dump(model, FICHIER_MODELE)
    print(f"[SUCCESS] Modele v3.0 sauvegarde: {FICHIER_MODELE}")
    
    print("\n" + "=" * 60)
    print("ENTRAINEMENT TERMINE AVEC SUCCES")
    print("=" * 60)
    print("\n[INFO] Prochaines etapes:")
    print("   1. Demarrer Kafka: docker-compose up -d")
    print("   2. Lancer le detecteur: python app/detector/detecteur.py")
    print("   3. Lancer le generateur: python app/generator/generateur.py")
    print("   4. Ouvrir le dashboard: streamlit run app/dashboard/dashboard.py")
    print("\n[TIP] Ou utilisez: start_app.bat")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()