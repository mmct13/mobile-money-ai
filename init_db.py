import sys
import os

# Ajouter le répertoire courant au path pour pouvoir importer app
sys.path.append(os.getcwd())

try:
    from app.database import init_db
    from app.config import DB_PATH
    
    print("[INFO] Verification de la base de donnees...")
    
    if os.path.isdir(DB_PATH):
        print(f"[WARNING] '{DB_PATH}' est un dossier (probablement cree par Docker). Suppression...")
        try:
            os.rmdir(DB_PATH)
            print(" - Dossier supprime avec succes.")
        except OSError as e:
            print(f"[ERROR] Impossible de supprimer le dossier '{DB_PATH}' : {e}")
            sys.exit(1)

    init_db()
    print("[SUCCESS] Base de donnees verifiee/creee.")
except Exception as e:
    print(f"[ERROR] Echec de l'initialisation de la base de donnees : {e}")
    sys.exit(1)
