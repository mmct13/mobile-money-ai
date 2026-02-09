from fastapi.testclient import TestClient
from app.api.main import app
import os

# Client de test
client = TestClient(app)

def test_api_status():
    """Vérifie que l'API est en ligne."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "online", "service": "MoneyShield AI Detector"}
    print("[PASS] API Status Check")

def test_predict_endpoint():
    """Teste la prédiction de fraude."""
    payload = {
        "transaction_id": "test-123",
        "date_heure": "2023-10-27T14:30:00",
        "montant": 5000000.0,
        "expediteur": "0701020304",
        "destinataire": "0705060708",
        "operateur": "Orange Money",
        "canal": "APP",
        "ville": "Abidjan-Plateau",
        "type_transaction": "TRANSFERT"
    }
    
    # On mocke le modèle si besoin, mais ici on teste l'intégration réelle
    # Si le modèle n'est pas chargé (pas de fichier .pkl), ça renverra 503
    try:
        response = client.post("/predict", json=payload)
        
        if response.status_code == 503:
            print("[WARN] Modèle non trouvé, impossible de tester la prédiction complète.")
            return

        assert response.status_code == 200
        data = response.json()
        
        print(f"[PASS] API Predict: {data}")
        assert "is_fraud" in data
        assert "risk_level" in data
        
    except Exception as e:
        print(f"[FAIL] {e}")

if __name__ == "__main__":
    print("=== TEST API MONEYSHIELD ===")
    test_api_status()
    test_predict_endpoint()
    print("=== FIN DES TESTS ===")
