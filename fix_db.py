import sqlite3
import os
from app.config import DB_PATH

def migrer_base_donnees():
    """Ajoute la colonne 'confiance' si elle manque."""
    print(f"[INFO] Verification de la base de donnees : {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print("[WARNING] Base de donnees introuvable. Rien a faire (elle sera creee au demarrage).")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Tenter de lire la colonne confiance
        cursor.execute("SELECT confiance FROM alertes LIMIT 1")
        print("[INFO] La colonne 'confiance' existe deja.")
    except sqlite3.OperationalError:
        print("[INFO] Colonne 'confiance' manquante. Ajout en cours...")
        try:
            cursor.execute("ALTER TABLE alertes ADD COLUMN confiance REAL DEFAULT 0.0")
            conn.commit()
            print("[SUCCESS] Colonne 'confiance' ajoutee avec succes !")
        except Exception as e:
            print(f"[ERROR] Erreur lors de la migration : {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrer_base_donnees()
