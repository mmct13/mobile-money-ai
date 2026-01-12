# Fichier: app/detector/classificateur_fraude.py
"""
Système de classification intelligent des motifs de fraude.
Utilise un système de scoring multi-critères pour identifier le type de fraude le plus probable.
"""
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class RegleFraude:
    """Représente une règle de détection de fraude."""
    nom: str
    description: str
    priorite: int  # Plus le nombre est élevé, plus c'est prioritaire
    
    def evaluer(self, transaction: dict, contexte: dict) -> float:
        """
        Évalue si cette règle correspond à la transaction.
        Retourne un score de 0.0 (pas de correspondance) à 1.0 (correspondance parfaite).
        
        Args:
            transaction: La transaction actuelle
            contexte: Dict contenant 'heure' (int) et 'historique' (list[dict])
        """
        raise NotImplementedError


class RegleVelocite(RegleFraude):
    """Détection de transactions répétitives rapides (Vélocité)."""
    
    def __init__(self):
        super().__init__(
            nom="Vélocité Excessive",
            description="Fréquence anormale: Multiples transactions sur le même numéro en peu de temps",
            priorite=8
        )
    
    def evaluer(self, transaction: dict, contexte: dict) -> float:
        historique = contexte.get('historique', [])
        if not historique:
            return 0.0
            
        score = 0.0
        # On cible l'expéditeur ou le destinataire qui reçoit trop
        sujet = transaction.get('expediteur')
        dest = transaction.get('destinataire')
        
        try:
            date_actuelle = datetime.fromisoformat(transaction['date_heure'])
        except:
            return 0.0
            
        # Paramètres de fenêtre temporaire (ex: 15 minutes)
        fenetre_temps = timedelta(minutes=15)
        
        count_exp = 0
        count_dest = 0
        
        for tx in historique:
            try:
                date_tx = datetime.fromisoformat(tx['date_heure'])
                delta = date_actuelle - date_tx
                # On regarde dans le passé, jusqu'à 15 min avant
                if timedelta(seconds=0) <= delta <= fenetre_temps:
                    if tx.get('expediteur') == sujet:
                        count_exp += 1
                    if tx.get('destinataire') == dest and dest is not None:
                        count_dest += 1
            except:
                continue
                
        # Analyse Vélocité Expéditeur (Harcelement, Spam, Vider un compte)
        if count_exp >= 3:
            score += 0.4
            if count_exp >= 5:
                score += 0.4  # Total 0.8
        
        # Analyse Vélocité Destinataire (Recevoir plein de petits paiements rapidement)
        if count_dest >= 3:
            score += 0.4
            if count_dest >= 5:
                score += 0.4

        return min(score, 1.0)


class RegleSchtroumpfage(RegleFraude):
    """Détection du schtroumpfage (Structuring/Accumulation)."""
    
    def __init__(self):
        super().__init__(
            nom="Accumulation Suspecte",
            description="Structuring: Dépôts multiples totalisant un montant élevé (Schtroumpfage)",
            priorite=9
        )
    
    def evaluer(self, transaction: dict, contexte: dict) -> float:
        # Uniquement pertinent pour les DEPOT ou TRANSFERT reçus
        if transaction.get('type_transaction') not in ["DEPOT", "TRANSFERT"]:
            return 0.0
            
        historique = contexte.get('historique', [])
        if not historique:
            return 0.0
            
        compte_cible = transaction.get('destinataire') # Celui qui reçoit l'argent
        mitant_actuel = transaction.get('montant', 0)
        
        try:
            date_actuelle = datetime.fromisoformat(transaction['date_heure'])
        except:
            return 0.0
            
        # Fenêtre d'analyse : 1 heure
        fenetre_temps = timedelta(hours=1)
        somme_cumulee = mitant_actuel
        nombre_tx = 1
        
        for tx in historique:
            try:
                # On cherche les transactions vers ce même compte
                if tx.get('destinataire') == compte_cible and tx.get('type_transaction') in ["DEPOT", "TRANSFERT"]:
                    date_tx = datetime.fromisoformat(tx['date_heure'])
                    delta = date_actuelle - date_tx
                    
                    if timedelta(seconds=0) <= delta <= fenetre_temps:
                        somme_cumulee += tx.get('montant', 0)
                        nombre_tx += 1
            except:
                continue
        
        score = 0.0
        
        # Si on dépasse 1 Million en cumulé avec plusieurs transactions
        if somme_cumulee > 1000000 and nombre_tx >= 2:
            score += 0.5
            # Si le montant cumulé est très élevé
            if somme_cumulee > 2000000:
                score += 0.3
            # Si beaucoup de petites transactions (signature typique schtroumpfage)
            if nombre_tx >= 3:
                score += 0.2
                
        return min(score, 1.0)


class RegleBroutage(RegleFraude):
    """Détection du broutage (cybercriminalité ivoirienne)."""
    
    def __init__(self):
        super().__init__(
            nom="Broutage",
            description="Cybercriminalité: Transactions nocturnes massives via smartphone",
            priorite=9
        )
    
    def evaluer(self, transaction: dict, contexte: dict) -> float:
        heure = contexte.get('heure', 0)
        score = 0.0
        montant = transaction.get('montant', 0)
        canal = transaction.get('canal', '')
        
        if 0 <= heure < 6:
            score += 0.4
        if montant > 200000:
            score += 0.3
            if montant > 500000:
                score += 0.1
        if canal in ["APP", "CARTE"]:
            score += 0.2
        if transaction.get('operateur') == "Wave":
            score += 0.1
        return min(score, 1.0)


class RegleSimSwap(RegleFraude):
    """Détection du vol d'identité par SIM Swap."""
    
    def __init__(self):
        super().__init__(
            nom="SIM Swap",
            description="Vol d'identité: Prise de contrôle du compte via nouvel SIM",
            priorite=10
        )
    
    def evaluer(self, transaction: dict, contexte: dict) -> float:
        heure = contexte.get('heure', 0)
        score = 0.0
        montant = transaction.get('montant', 0)
        canal = transaction.get('canal', '')
        type_trans = transaction.get('type_transaction', '')
        
        if montant > 500000:
            score += 0.3
            if montant > 1000000:
                score += 0.2
        if canal == "AGENT":
            score += 0.3
        elif canal == "USSD":
            score += 0.2
        if 2 <= heure <= 7:
            score += 0.2
        if type_trans in ["RETRAIT", "TRANSFERT"]:
            score += 0.1
        return min(score, 1.0)


class RegleBlanchiment(RegleFraude):
    """Détection du blanchiment d'argent."""
    
    def __init__(self):
        super().__init__(
            nom="Blanchiment",
            description="Flux financiers atypiques: Montants massifs en zones non urbaines",
            priorite=10
        )
    
    def evaluer(self, transaction: dict, contexte: dict) -> float:
        heure = contexte.get('heure', 0)
        score = 0.0
        montant = transaction.get('montant', 0)
        ville = transaction.get('ville', '')
        canal = transaction.get('canal', '')
        type_trans = transaction.get('type_transaction', '')
        
        if montant > 1000000:
            score += 0.4
            if montant > 2000000:
                score += 0.2
        # Zones rurales spécifiques
        zones_sensibles = ["San-Pédro", "Soubré", "Odienné", "Bondoukou", "Séguéla"]
        if ville in zones_sensibles:
            score += 0.3
        if canal == "AGENT":
            score += 0.2
        if type_trans == "DEPOT":
            score += 0.1
        return min(score, 1.0)


class RegleIngenierieSociale(RegleFraude):
    """Détection de l'ingénierie sociale (phishing, vishing)."""
    
    def __init__(self):
        super().__init__(
            nom="Ingénierie Sociale",
            description="Arnaques par SMS/Appels: Faux gains, faux frais, phishing",
            priorite=7
        )
    
    def evaluer(self, transaction: dict, contexte: dict) -> float:
        heure = contexte.get('heure', 0)
        score = 0.0
        montant = transaction.get('montant', 0)
        canal = transaction.get('canal', '')
        type_trans = transaction.get('type_transaction', '')
        
        if 50000 <= montant <= 300000:
            score += 0.3
        if canal == "USSD":
            score += 0.4
        if 8 <= heure <= 20:
            score += 0.2
        if type_trans in ["TRANSFERT", "PAIEMENT_MARCHAND"]:
            score += 0.1
        return min(score, 1.0)


class RegleVolPhysique(RegleFraude):
    """Détection du vol de téléphone."""
    
    def __init__(self):
        super().__init__(
            nom="Vol Physique",
            description="Vol de téléphone: Retraits rapides après vol",
            priorite=8
        )
    
    def evaluer(self, transaction: dict, contexte: dict) -> float:
        heure = contexte.get('heure', 0)
        score = 0.0
        montant = transaction.get('montant', 0)
        canal = transaction.get('canal', '')
        type_trans = transaction.get('type_transaction', '')
        ville = transaction.get('ville', '')
        
        if 18 <= heure <= 23:
            score += 0.3
        if 50000 <= montant <= 300000:
            score += 0.2
        if type_trans == "RETRAIT" and canal == "AGENT":
            score += 0.3
        zones_risque = ["Abidjan-Abobo", "Abidjan-Adjamé", "Abidjan-Yopougon"]
        if ville in zones_risque:
            score += 0.2
        return min(score, 1.0)


class RegleFraudeAgent(RegleFraude):
    """Détection de la fraude par un agent Mobile Money."""
    
    def __init__(self):
        super().__init__(
            nom="Fraude Agent",
            description="Détournement par agent: Transactions suspectes en fin de journée",
            priorite=8
        )
    
    def evaluer(self, transaction: dict, contexte: dict) -> float:
        heure = contexte.get('heure', 0)
        score = 0.0
        montant = transaction.get('montant', 0)
        canal = transaction.get('canal', '')
        type_trans = transaction.get('type_transaction', '')
        
        if canal != "AGENT":
            return 0.0
        score += 0.3
        if 18 <= heure <= 21:
            score += 0.3
        if 100000 <= montant <= 500000:
            score += 0.2
        if type_trans == "DEPOT":
            score += 0.2
        return min(score, 1.0)


class RegleAnomalieBehaviorale(RegleFraude):
    """Règle par défaut pour anomalies détectées par l'IA sans motif clair."""
    
    def __init__(self):
        super().__init__(
            nom="Anomalie Comportementale",
            description="Comportement suspect détecté par l'IA sans correspondance claire",
            priorite=1
        )
    
    def evaluer(self, transaction: dict, contexte: dict) -> float:
        return 0.3


class ClassificateurFraude:
    """
    Classificateur intelligent de fraudes avec système de scoring multi-critères.
    """
    
    def __init__(self):
        # Ordre important: Velocity/Accumulation en premier car patterns forts
        self.regles = [
            RegleSchtroumpfage(),
            RegleVelocite(),
            RegleBroutage(),
            RegleSimSwap(),
            RegleBlanchiment(),
            RegleIngenierieSociale(),
            RegleVolPhysique(),
            RegleFraudeAgent(),
            RegleAnomalieBehaviorale()
        ]
    
    def classifier(self, transaction: dict, contexte: dict) -> Tuple[str, str, float]:
        """
        Classifie une transaction frauduleuse.
        """
        resultats = []
        for regle in self.regles:
            try:
                score = regle.evaluer(transaction, contexte)
                if score > 0:
                    resultats.append((regle, score))
            except Exception as e:
                print(f"Erreur règle {regle.nom}: {e}")
                continue
        
        # Trier par score décroissant, puis par priorité
        resultats.sort(key=lambda x: (x[1], x[0].priorite), reverse=True)
        
        if resultats:
            meilleure_regle, meilleur_score = resultats[0]
            return (meilleure_regle.nom, meilleure_regle.description, meilleur_score)
        else:
            regle_defaut = self.regles[-1]
            return (regle_defaut.nom, regle_defaut.description, 0.3)

    def classifier_avec_details(self, transaction: dict, contexte: dict) -> Dict:
        """Version détaillée pour debugging."""
        resultats = {}
        for regle in self.regles:
            score = regle.evaluer(transaction, contexte)
            resultats[regle.nom] = {
                "score": score,
                "description": regle.description,
                "priorite": regle.priorite
            }
        
        motif, description, confiance = self.classifier(transaction, contexte)
        return {
            "motif_principal": motif,
            "description": description,
            "confiance": confiance,
            "tous_les_scores": resultats
        }
