import sqlite3
import os
from app.config import DB_PATH

def migrer_base_donnees():
    """Ajoute la colonne 'confiance' si elle manque."""
    print(f"🔧 Vérification de la base de données : {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print("⚠️  Base de données introuvable. Rien à faire (elle sera créée au démarrage).")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Tenter de lire la colonne confiance
        cursor.execute("SELECT confiance FROM alertes LIMIT 1")
        print("✅  La colonne 'confiance' existe déjà.")
    except sqlite3.OperationalError:
        print("🛠️  Colonne 'confiance' manquante. Ajout en cours...")
        try:
            cursor.execute("ALTER TABLE alertes ADD COLUMN confiance REAL DEFAULT 0.0")
            conn.commit()
            print("✅  Colonne 'confiance' ajoutée avec succès !")
        except Exception as e:
            print(f"❌  Erreur lors de la migration : {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrer_base_donnees()
