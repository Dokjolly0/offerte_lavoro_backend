from utils.database.db_config import DBConfig
from utils.database.db_connection import DBConnection
from utils.database.db_tables import DBTables

if __name__ == "__main__":
    try:
        # Configurazione del database
        config = DBConfig(path="./database", name="job_offert.db")
        # Gestione della connessione
        connection = DBConnection(config)
        connection.create_database()
        connection.connect()
        # Operazioni sulle tabelle
        tables = DBTables(connection)
        tables.create_jobs_table()
        tables.insert_job(titolo="Sviluppatore Python", descrizione_breve="Cerchiamo uno sviluppatore Python con esperienza", azienda="Python Srl", provincia="MI", data_inserimento="2021-09-01", smart_working="si", retribuzione_lorda=30000, tipologia_contratto="Full-time")
        # Recupera e stampa tutti i job
        jobs = tables.fetch_all_jobs()
        print("Jobs nel database:", jobs)
    except Exception as e:
        print(f"Errore: {e}")
        exit()
    finally:
        # Chiudi la connessione
        connection.close()
