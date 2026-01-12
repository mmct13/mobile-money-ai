# Fichier: app/database.py
import sqlite3
from app.config import DB_PATH

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS alertes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL,
            date_heure TEXT,
            montant INTEGER,
            expediteur TEXT,
            ville TEXT,
            operateur TEXT,
            canal TEXT,
            type_trans TEXT,
            score REAL,
            motif TEXT,
            confiance REAL DEFAULT 0.0
        )
    ''')
    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect(DB_PATH)