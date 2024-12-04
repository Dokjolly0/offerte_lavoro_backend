import sqlite3
from utils.database.db_connection import DBConnection

class DBTables:
    """Classe per gestire le operazioni sulle tabelle del database."""
    def __init__(self, connection: DBConnection):
        self.connection = connection

    def create_jobs_table(self):
        """Crea la tabella jobs con i campi specificati se non esiste."""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS jobs (
            OffertaLavoroID INTEGER PRIMARY KEY AUTOINCREMENT,
            Titolo TEXT NOT NULL,
            DescrizioneBreve TEXT,
            Azienda TEXT NOT NULL,
            Provincia TEXT,
            DataInserimento DATE NOT NULL,
            SmartWorking TEXT CHECK(SmartWorking IN ('si', 'no')),
            RetribuzioneLorda REAL,
            TipologiaContratto TEXT
        )
        """
        self.execute_query(create_table_query)
        print("Tabella jobs creata o già esistente.")

    def insert_job(self, titolo, descrizione_breve, azienda, provincia, data_inserimento, smart_working, retribuzione_lorda, tipologia_contratto):
        """Inserisce un record nella tabella jobs."""
        insert_query = """
        INSERT INTO jobs (Titolo, DescrizioneBreve, Azienda, Provincia, DataInserimento, SmartWorking, RetribuzioneLorda, TipologiaContratto)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.execute_query(insert_query, (titolo, descrizione_breve, azienda, provincia, data_inserimento, smart_working, retribuzione_lorda, tipologia_contratto))
        print(f"Job '{titolo}' inserito con successo.")


    def fetch_all_jobs(self):
        """Recupera tutti i record dalla tabella jobs."""
        select_query = "SELECT * FROM jobs"
        return self.execute_query(select_query)
    
    def execute_query(self, query, params=None):
        """Esegue una query sul database."""
        if not self.connection.connection:
            print("La connessione al database non è aperta.")
            return None
        try:
            cursor = self.connection.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.connection.commit()
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Errore durante l'esecuzione della query: {e}")
            return None
        except Exception as e:
            print(f"Errore generico: {e}")
            return None