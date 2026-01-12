# Fichier: test_classificateur.py
"""
Script de test pour vérifier le classificateur de fraude intelligent.
Inclut maintenant les tests de vélocité et d'accumulation (Schtroumpfage).
"""
from app.detector.classificateur_fraude import ClassificateurFraude
from datetime import datetime, timedelta

def get_base_contexte(heure=12):
    """Génère un contexte de base."""
    return {
        'heure': heure,
        'historique': []
    }

def test_velocite():
    """Test de détection de vélocité excessive."""
    classificateur = ClassificateurFraude()
    
    # Numéro cible
    target_num = "0701020304"
    now = datetime.now()
    
    # Création d'un historique avec 4 transactions récentes ( < 15 min)
    historique = []
    for i in range(4):
        tx_time = now - timedelta(minutes=i*2) # 0, 2, 4, 6 mins ago
        historique.append({
            'date_heure': tx_time.isoformat(),
            'expediteur': target_num,
            'destinataire': "0101010101",
            'montant': 5000,
            'operateur': 'Orange Money'
        })
    
    # La transaction actuelle (la 5ème)
    transaction = {
        'date_heure': now.isoformat(),
        'expediteur': target_num,
        'destinataire': "0101010101",
        'montant': 5000,
        'operateur': 'Orange Money',
        'type_transaction': 'TRANSFERT'
    }
    
    contexte = {
        'heure': now.hour,
        'historique': historique
    }
    
    motif, desc, confiance = classificateur.classifier(transaction, contexte)
    print(f"\n✅ Test Vélocité:")
    print(f"   Motif: {motif}")
    print(f"   Confiance: {confiance*100:.1f}%")
    assert motif == "Vélocité Excessive", f"Attendu 'Vélocité Excessive', reçu '{motif}'"
    print(f"   ✓ Test réussi!")

def test_schtroumpfage():
    """Test de détection accumulation/structuring."""
    classificateur = ClassificateurFraude()
    
    target_account = "0505050505"
    now = datetime.now()
    
    # Historique: 3 dépôts de 400,000 (Total 1.2M) en moins d'une heure
    historique = []
    for i in range(3):
        tx_time = now - timedelta(minutes=10 + i*5)
        historique.append({
            'date_heure': tx_time.isoformat(),
            'destinataire': target_account,
            'montant': 400000,
            'type_transaction': 'DEPOT',
            'operateur': 'MTN MoMo'
        })
        
    transaction = {
        'date_heure': now.isoformat(),
        'destinataire': target_account,
        'montant': 400000, # +400k = 1.6M total
        'type_transaction': 'DEPOT',
        'operateur': 'MTN MoMo',
        'canal': 'AGENT'
    }
    
    contexte = {
        'heure': now.hour,
        'historique': historique
    }
    
    motif, desc, confiance = classificateur.classifier(transaction, contexte)
    print(f"\n✅ Test Schtroumpfage:")
    print(f"   Motif: {motif}")
    print(f"   Confiance: {confiance*100:.1f}%")
    assert motif == "Accumulation Suspecte", f"Attendu 'Accumulation Suspecte', reçu '{motif}'"
    print(f"   ✓ Test réussi!")

def test_broutage():
    """Test de détection du broutage."""
    classificateur = ClassificateurFraude()
    transaction = {
        'montant': 500000,
        'canal': 'APP',
        'operateur': 'Wave',
        'type_transaction': 'RETRAIT',
        'ville': 'Abidjan-Yopougon'
    }
    # Heure 3h du matin
    contexte = get_base_contexte(heure=3)
    
    motif, desc, confiance = classificateur.classifier(transaction, contexte)
    print(f"\n✅ Test Broutage:")
    print(f"   Motif: {motif}")
    assert motif == "Broutage", f"Attendu 'Broutage', reçu '{motif}'"
    print(f"   ✓ Test réussi!")

# ... Adaptation des autres tests avec 'contexte' ...

def test_sim_swap():
    classificateur = ClassificateurFraude()
    transaction = {
        'montant': 800000,
        'canal': 'AGENT',
        'operateur': 'MTN MoMo',
        'type_transaction': 'RETRAIT',
        'ville': 'Bouaké'
    }
    contexte = get_base_contexte(heure=5)
    motif, _, _ = classificateur.classifier(transaction, contexte)
    assert motif == "SIM Swap"
    print("\n✅ Test SIM Swap: ✓ Réussi")

def test_blanchiment():
    classificateur = ClassificateurFraude()
    transaction = {
        'montant': 2500000,
        'canal': 'AGENT',
        'operateur': 'Orange Money',
        'type_transaction': 'DEPOT',
        'ville': 'Soubré'
    }
    contexte = get_base_contexte(heure=14)
    motif, _, _ = classificateur.classifier(transaction, contexte)
    assert motif == "Blanchiment"
    print("\n✅ Test Blanchiment: ✓ Réussi")

if __name__ == "__main__":
    print("=" * 60)
    print("🛡️  MONEYSHIELD CI - Tests des Patterns Temporels")
    print("=" * 60)
    
    try:
        test_velocite()
        test_schtroumpfage()
        test_broutage()
        test_sim_swap()
        test_blanchiment()
        
        print("\n" + "=" * 60)
        print("✅ TOUS LES TESTS ONT RÉUSSI!")
        print("=" * 60 + "\n")
    except AssertionError as e:
        print(f"\n❌ ERREUR: {e}\n")
    except Exception as e:
        print(f"\n❌ ERREUR INATTENDUE: {e}\n")
        import traceback
        traceback.print_exc()
