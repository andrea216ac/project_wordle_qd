# src/database/init_db.py
from src.database.db import engine, Base

# È FONDAMENTALE importare i modelli qui, altrimenti SQLAlchemy 
# non sa che esistono e creerà un database vuoto!
from src.database.models import User, Game 

def init_database():
    print("Creazione del database in corso...")
    
    # Questo è il comando magico che traduce le classi Python in tabelle SQL
    Base.metadata.create_all(bind=engine)
    
    print("Database 'wordle.db' e tabelle creati con successo! 🎉")

if __name__ == "__main__":
    init_database()