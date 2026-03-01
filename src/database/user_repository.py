from sqlalchemy.orm import Session
from src.database.models import User

class UserRepository:
    """
    Questa classe gestisce tutte le operazioni nel database per la tabella 'users'.
    Isola la logica di accesso ai dati dal resto dell'applicazione.
    """
    
    def __init__(self, session: Session):
        # Riceve la sessione (la "connessione" attiva) quando viene creata
        self.session = session

    def get_user_by_username(self, username: str) -> User | None:
        """Cerca un utente per nome. Restituisce l'oggetto User se esiste, altrimenti None."""
        return self.session.query(User).filter(User.username == username).first()

    def create_user(self, username: str) -> User:
        """
        Crea un nuovo utente. Se l'utente esiste già (essendo UNIQUE), 
        lo recupera semplicemente senza mandare in crash il programma.
        """
        # 1. Controlliamo se il giocatore esiste già
        existing_user = self.get_user_by_username(username)
        if existing_user:
            return existing_user  # Se esiste, facciamo un "login" automatico

        # 2. Se non esiste, creiamo il nuovo oggetto Python
        new_user = User(username=username)
        
        # 3. Lo aggiungiamo alla sessione e salviamo sul database (commit)
        self.session.add(new_user)
        self.session.commit()
        
        # 4. Aggiorniamo l'oggetto per ottenere l'ID generato automaticamente da SQLite
        self.session.refresh(new_user)
        
        return new_user