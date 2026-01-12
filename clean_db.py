import os
from app.config import DB_PATH
from app.database import init_db

def clean_database():
    print(f"Action : Suppression de la base de donnees : {DB_PATH}")
    
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
            print("Succes : Base de donnees supprimee.")
        except Exception as e:
            print(f"Erreur : Impossible de supprimer la base de donnees : {e}")
            return
    else:
        print("Info : Aucune base de donnees trouvee.")

    print("Action : Re-initialisation de la base de donnees...")
    try:
        init_db()
        print("Succes : Base de donnees re-creee et vide.")
    except Exception as e:
        print(f"Erreur : Echec de la re-initialisation : {e}")

if __name__ == "__main__":
    clean_database()
