import sys
import os

REQUIRED_FILES = [
    "app/database.py",
    "app/config.py",
    "app/dashboard/dashboard.py",
    "app/detector/detecteur.py",
    "app/detector/classificateur_fraude.py",
    "app/generator/generateur.py",
    "moneyshield.db"
]

def verify_project_structure():
    print("Verifying project structure...")
    missing = []
    for f in REQUIRED_FILES:
        if os.path.exists(f):
            print(f" [OK] Found {f}")
        else:
            print(f" [MISSING] {f}")
            missing.append(f)
            
    if missing:
        print(f"\n[ERROR] Missing {len(missing)} critical files.")
        return 1
    
    print("\nProject structure verified.")
    return 0

if __name__ == "__main__":
    sys.exit(verify_project_structure())
