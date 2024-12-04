import sqlite3
from utils.database.db_config import DBConfig

class DBConnection:
    """Classe per gestire la connessione al database."""
    def __init__(self, config: DBConfig):
        self.config = config
        self.connection = None

    def connect(self):
        """Apre una connessione al database."""
        try:
            self.connection = sqlite3.connect(self.config.full_path, check_same_thread=False)
            print("Connessione al database riuscita, path:", self.config.full_path)
        except sqlite3.Error as e:
            raise Exception(f"Errore durante la connessione al database: {e}")

    def close(self):
        """Chiude la connessione al database."""
        if self.connection:
            try:
                self.connection.close()
                print("Connessione al database chiusa.")
            except sqlite3.Error as e:
                raise Exception(f"Errore durante la chiusura della connessione: {e}")
            finally:
                self.connection = None

    def create_database(self):
        """Crea il database se non esiste."""
        try:
            with open(self.config.full_path, 'a'):
                pass  # Il file viene creato se non esiste
            print(f"Database {self.config.name} creato (se non esisteva).")
        except IOError as e:
            raise Exception(f"Errore durante la creazione del database: {e}")
