import logging
import time
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import joblib
import pandas as pd
import os
from datetime import datetime
from collections import deque

from app.config import MAP_VILLES, MAP_TYPES, MAP_OPERATEURS, MAP_CANAUX
from app.detector.classificateur_fraude import ClassificateurFraude

# --- CONFIGURATION LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# --- CONFIGURATION APP ---
app = FastAPI(
    title="MoneyShield AI API",
    description="API de détection de fraude Mobile Money en temps réel",
    version="1.0.0"
)

# --- CHARGEMENT MODELE ---
DOSSIER_COURANT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # app/
FICHIER_MODELE = os.path.join(DOSSIER_COURANT, "detector", "modele_fraude.pkl")

model = None
try:
    if os.path.exists(FICHIER_MODELE):
        model = joblib.load(FICHIER_MODELE)
        logger.info(f"Modèle IA chargé depuis {FICHIER_MODELE}")
    else:
        logger.error(f"Modèle IA introuvable à {FICHIER_MODELE}")
except Exception as e:
    logger.error(f"Erreur chargement modèle: {e}")

# Initialisation Classificateur
classificateur = ClassificateurFraude()

# --- SCHEMAS DE DONNEES (Pydantic) ---
class TransactionInput(BaseModel):
    transaction_id: str = Field(..., description="ID unique de la transaction")
    date_heure: str = Field(..., description="Date et heure ISO 8601")
    montant: float = Field(..., ge=0, description="Montant de la transaction")
    expediteur: str = Field(..., description="Numéro expéditeur")
    destinataire: Optional[str] = Field(None, description="Numéro destinataire")
    operateur: str = Field(..., description="Opérateur (Orange Money, MTN MoMo, etc.)")
    canal: str = Field(..., description="Canal (USSD, APP, AGENT, CARTE)")
    ville: str = Field(..., description="Ville de la transaction")
    type_transaction: str = Field(..., description="Type (DEPOT, RETRAIT, TRANSFERT, PAIEMENT_MARCHAND)")

class FraudPrediction(BaseModel):
    is_fraud: bool
    probability: float
    risk_level: str
    motif: Optional[str] = None
    description: Optional[str] = None
    confidence: Optional[float] = None

# --- HISTORIQUE POUR CONTEXTE (SIMPLIFIÉ) ---
# Dans une vraie API, utiliser Redis ou une DB rapide
# Ici on garde un petit historique en mémoire locale pour la démo
historique_transactions = deque(maxlen=1000)

@app.on_event("startup")
async def startup_event():
    logger.info("Démarrage de l'API MoneyShield AI")

@app.get("/")
def read_root():
    return {"status": "online", "service": "MoneyShield AI Detector"}

@app.post("/predict", response_model=FraudPrediction)
def predict_fraud(transaction: TransactionInput):
    if model is None:
        raise HTTPException(status_code=503, detail="Modèle IA non chargé")

    # 1. Conversion Pydantic -> Dict
    tx_dict = transaction.dict()
    
    # Ajout à l'historique pour le contexte
    # Note: Dans un worker uvicorn multiple, cet historique est par process (limitation connue ici)
    historique_transactions.appendleft(tx_dict)

    try:
        # 2. Preprocessing (Identique au detecteur.py)
        dt = datetime.fromisoformat(tx_dict['date_heure'])
        heure = dt.hour

        ville_code = MAP_VILLES.get(tx_dict['ville'], -1)
        type_code = MAP_TYPES.get(tx_dict['type_transaction'], -1)
        op_code = MAP_OPERATEURS.get(tx_dict['operateur'], -1)
        canal_code = MAP_CANAUX.get(tx_dict['canal'], -1)

        features = pd.DataFrame([{
            "montant": tx_dict['montant'],
            "heure": heure,
            "ville_code": ville_code,
            "type_code": type_code,
            "operateur_code": op_code,
            "canal_code": canal_code
        }])

        # 3. Prédiction IA
        proba_fraude = model.predict_proba(features)[0][1]
        is_fraud = proba_fraude > 0.5

        result = {
            "is_fraud": bool(is_fraud),
            "probability": float(proba_fraude),
            "risk_level": "LOW"
        }

        if is_fraud:
            # 4. Classification
            contexte = {
                'heure': heure,
                'historique': list(historique_transactions)
            }
            motif, desc, conf_regles = classificateur.classifier(tx_dict, contexte)
            
            # Confiance globale
            confiance_globale = (proba_fraude + conf_regles) / 2

            result.update({
                "risk_level": "HIGH" if confiance_globale > 0.8 else "MEDIUM",
                "motif": motif,
                "description": desc,
                "confidence": float(confiance_globale)
            })
            
            logger.warning(f"Fraude détectée: {motif} ({confiance_globale:.2f})")
        
        return result

    except Exception as e:
        logger.error(f"Erreur prédiction: {e}")
        raise HTTPException(status_code=500, detail=str(e))
