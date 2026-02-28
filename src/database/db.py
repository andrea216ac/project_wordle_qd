from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# 1. Definiamo dove verrà salvato il database. 
# Creo un file 'wordle.db' nella cartella principale (che abbiamo già messo nel .gitignore!)
DATABASE_URL = "sqlite:///wordle.db"

# 2. Creiamo il "motore" di SQLAlchemy. 
# È lui che "parla" con SQLite. (Metto echo=false per un migliore debug tramite lettura del terminale)
engine = create_engine(DATABASE_URL, echo=False)

# 3. Creiamo la "Fabbrica delle Sessioni"
# Una sessione è una singola "conversazione" con il database (es. per salvare una partita)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Creiamo la Base
# Da questa classe 'Base' erediteranno tutte le nostre tabelle (Utenti, Partite, ecc.)
Base = declarative_base()

# 5. Funzione di utilità per aprire e chiudere la connessione in modo sicuro
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()