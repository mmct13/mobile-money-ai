# Fichier: app/config.py
import os

# Chemins dynamiques (Peu importe où on lance le script, il trouvera la DB)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "moneyshield.db")

# Constantes partagées
KAFKA_TOPIC = "flux_mobile_money"
MAP_VILLES = {
    "Abidjan-Yopougon": 0, "Abidjan-Abobo": 1, "Abidjan-Cocody": 2,
    "Abidjan-Plateau": 3, "Abidjan-Marcory": 4, "Abidjan-Koumassi": 5, "Abidjan-Adjamé": 6,
    "Bouaké": 7, "Daloa": 8, "Yamoussoukro": 9, "San-Pédro": 10,
    "Korhogo": 11, "Man": 12, "Gagnoa": 13, "Grand-Bassam": 14,
    "Soubré": 15, "Aboisso": 16, "Odienné": 17, "Bondoukou": 18, "Séguéla": 19,
    
    # Nouvelles communes Abidjan
    "Abidjan-Port-Bouët": 20, "Abidjan-Treichville": 21, "Abidjan-Attécoubé": 22,
    "Abidjan-Anyama": 23, "Abidjan-Bingerville": 24, "Abidjan-Songon": 25,

    # Villes de l'intérieur supplémentaires
    "Divo": 26, "Abengourou": 27, "Katiola": 28, "Boundiali": 29, 
    "Ferkessédougou": 30, "Issia": 31, "Sinfra": 32, "Oumé": 33, 
    "Duékoué": 34, "Tiassalé": 35
}
MAP_TYPES = {"DEPOT": 0, "TRANSFERT": 1, "RETRAIT": 2, "PAIEMENT_MARCHAND": 3}
MAP_OPERATEURS = {"Orange Money": 0, "MTN MoMo": 1, "Moov Money": 2, "Wave": 3}
MAP_CANAUX = {"USSD": 0, "APP": 1, "CARTE": 2, "AGENT": 3}