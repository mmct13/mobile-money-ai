"""
Script pour visualiser le contenu de la base de données SQLite MoneyShield CI
"""
import sqlite3
import sys
from pathlib import Path

# Chemin de la base de données
DB_PATH = Path(__file__).parent / "moneyshield.db"

def afficher_menu():
    """Affiche le menu principal"""
    print("\n" + "=" * 60)
    print("    MONEYSHIELD CI - Explorateur de Base de Données")
    print("=" * 60)
    print("\n1. Afficher toutes les tables")
    print("2. Afficher le schéma de la table 'alertes'")
    print("3. Compter les alertes")
    print("4. Afficher les dernières alertes")
    print("5. Afficher les statistiques")
    print("6. Rechercher des alertes par montant")
    print("7. Afficher les alertes par ville")
    print("8. Afficher les alertes par opérateur")
    print("0. Quitter")
    print("=" * 60)

def lister_tables():
    """Liste toutes les tables de la base de données"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    conn.close()
    
    print("\n📋 Tables disponibles:")
    for table in tables:
        print(f"   - {table[0]}")

def afficher_schema():
    """Affiche le schéma de la table alertes"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(alertes)")
    colonnes = cursor.fetchall()
    conn.close()
    
    print("\n📊 Schéma de la table 'alertes':")
    print(f"{'ID':<5} {'Nom':<20} {'Type':<15} {'Non Null':<10} {'Défaut'}")
    print("-" * 70)
    for col in colonnes:
        print(f"{col[0]:<5} {col[1]:<20} {col[2]:<15} {col[3]:<10} {col[4] or ''}")

def compter_alertes():
    """Compte le nombre total d'alertes"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM alertes")
    count = cursor.fetchone()[0]
    conn.close()
    
    print(f"\n🔢 Nombre total d'alertes: {count:,}".replace(",", " "))

def afficher_dernieres_alertes(limite=10):
    """Affiche les dernières alertes"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, date_heure, montant, expediteur, ville, operateur, canal, type_trans, score, motif
        FROM alertes
        ORDER BY id DESC
        LIMIT ?
    """, (limite,))
    
    alertes = cursor.fetchall()
    conn.close()
    
    print(f"\n🚨 Dernières {limite} alertes détectées:")
    print("-" * 150)
    for alerte in alertes:
        print(f"ID: {alerte['id']} | {alerte['date_heure']} | {alerte['montant']:,} F | {alerte['expediteur']}"
              f" | {alerte['ville']} | {alerte['operateur']} | {alerte['canal']} | {alerte['type_trans']}"
              f" | Score: {alerte['score']:.3f} | {alerte['motif']}".replace(",", " "))

def afficher_statistiques():
    """Affiche des statistiques sur les alertes"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Total alertes
    cursor.execute("SELECT COUNT(*) FROM alertes")
    total = cursor.fetchone()[0]
    
    # Montant moyen
    cursor.execute("SELECT AVG(montant) FROM alertes")
    montant_moyen = cursor.fetchone()[0] or 0
    
    # Montant max
    cursor.execute("SELECT MAX(montant) FROM alertes")
    montant_max = cursor.fetchone()[0] or 0
    
    # Par motif
    cursor.execute("SELECT motif, COUNT(*) FROM alertes GROUP BY motif ORDER BY COUNT(*) DESC")
    par_motif = cursor.fetchall()
    
    # Par opérateur
    cursor.execute("SELECT operateur, COUNT(*) FROM alertes GROUP BY operateur ORDER BY COUNT(*) DESC")
    par_operateur = cursor.fetchall()
    
    conn.close()
    
    print("\n📊 STATISTIQUES DES ALERTES")
    print("=" * 60)
    print(f"Total d'alertes: {total:,}".replace(",", " "))
    print(f"Montant moyen: {montant_moyen:,.0f} F".replace(",", " "))
    print(f"Montant maximum: {montant_max:,.0f} F".replace(",", " "))
    
    print("\n📍 Répartition par motif:")
    for motif, count in par_motif:
        pourcentage = (count / total * 100) if total > 0 else 0
        print(f"   {motif:<35} : {count:>5} ({pourcentage:.1f}%)")
    
    print("\n📱 Répartition par opérateur:")
    for operateur, count in par_operateur:
        pourcentage = (count / total * 100) if total > 0 else 0
        print(f"   {operateur:<20} : {count:>5} ({pourcentage:.1f}%)")

def rechercher_par_montant():
    """Recherche des alertes par montant"""
    try:
        montant_min = int(input("\n💰 Montant minimum (F): "))
        montant_max = int(input("💰 Montant maximum (F): "))
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, date_heure, montant, expediteur, ville, operateur, motif
            FROM alertes
            WHERE montant BETWEEN ? AND ?
            ORDER BY montant DESC
            LIMIT 20
        """, (montant_min, montant_max))
        
        alertes = cursor.fetchall()
        conn.close()
        
        print(f"\n🔍 Alertes entre {montant_min:,} F et {montant_max:,} F:".replace(",", " "))
        print("-" * 120)
        for alerte in alertes:
            print(f"ID: {alerte['id']} | {alerte['date_heure']} | {alerte['montant']:,} F | {alerte['expediteur']}"
                  f" | {alerte['ville']} | {alerte['operateur']} | {alerte['motif']}".replace(",", " "))
        
        print(f"\nTotal: {len(alertes)} alertes trouvées")
        
    except ValueError:
        print("❌ Erreur: Veuillez entrer des nombres valides")

def afficher_par_ville():
    """Affiche les alertes groupées par ville"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT ville, COUNT(*) as nb, AVG(montant) as montant_moyen
        FROM alertes
        GROUP BY ville
        ORDER BY nb DESC
    """)
    
    resultats = cursor.fetchall()
    conn.close()
    
    print("\n📍 Alertes par ville:")
    print(f"{'Ville':<25} {'Nombre':<10} {'Montant moyen'}")
    print("-" * 60)
    for ville, nb, montant_moyen in resultats:
        print(f"{ville:<25} {nb:<10} {montant_moyen:,.0f} F".replace(",", " "))

def afficher_par_operateur():
    """Affiche les alertes groupées par opérateur"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT operateur, COUNT(*) as nb, AVG(montant) as montant_moyen
        FROM alertes
        GROUP BY operateur
        ORDER BY nb DESC
    """)
    
    resultats = cursor.fetchall()
    conn.close()
    
    print("\n📱 Alertes par opérateur:")
    print(f"{'Opérateur':<20} {'Nombre':<10} {'Montant moyen'}")
    print("-" * 60)
    for operateur, nb, montant_moyen in resultats:
        print(f"{operateur:<20} {nb:<10} {montant_moyen:,.0f} F".replace(",", " "))

def main():
    """Point d'entrée principal"""
    if not DB_PATH.exists():
        print(f"❌ Erreur: La base de données '{DB_PATH}' n'existe pas.")
        print("Veuillez lancer le détecteur pour créer la base de données.")
        sys.exit(1)
    
    actions = {
        '1': lister_tables,
        '2': afficher_schema,
        '3': compter_alertes,
        '4': lambda: afficher_dernieres_alertes(int(input("Nombre d'alertes à afficher: ") or 10)),
        '5': afficher_statistiques,
        '6': rechercher_par_montant,
        '7': afficher_par_ville,
        '8': afficher_par_operateur,
    }
    
    while True:
        afficher_menu()
        choix = input("\nVotre choix: ").strip()
        
        if choix == '0':
            print("\n👋 Au revoir!")
            break
        
        if choix in actions:
            try:
                actions[choix]()
            except Exception as e:
                print(f"\n❌ Erreur: {e}")
        else:
            print("\n❌ Choix invalide!")
        
        input("\nAppuyez sur Entrée pour continuer...")

if __name__ == "__main__":
    main()
