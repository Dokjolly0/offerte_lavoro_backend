import os
import sys
from flask import Flask, request, jsonify
from utils.database.db_config import DBConfig
from utils.database.db_connection import DBConnection
from utils.database.db_tables import DBTables
import datetime
from flask_cors import CORS

app = Flask(__name__)
# Abilita CORS per tutte le origini (puoi anche specificare solo certe origini)
CORS(app, resources={r"/*": {"origins": "*"}})

# Ottieni il percorso assoluto del file database.job_offert.db
base_dir = os.path.abspath(os.path.dirname(__file__))  # Percorso della cartella che contiene main.py
db_path = os.path.join(base_dir, 'database')  # Aggiungi solo la directory per il database
# Verifica se la directory esiste
if not os.path.isdir(db_path):
    print(f"Errore: Il percorso {db_path} non esiste.")
    sys.exit(1)  # Uscita dal programma con errore
# Configurazione del database con il percorso corretto
config = DBConfig(path=db_path, name="job_offert.db")
db_connection = DBConnection(config)
db_connection.connect()
# Creazione delle tabelle se non esistono
db_tables = DBTables(db_connection)
db_tables.create_jobs_table()

@app.route('/job', methods=['GET'])
def get_job():
    """
    Restituisce un'offerta di lavoro specifica in base all'ID.
    """
    offerta_id = request.args.get('id', type=int)
    if not offerta_id:
        return jsonify({"message": "ID offerta di lavoro non fornito"}), 400
    select_query = "SELECT * FROM jobs WHERE OffertaLavoroID = ?"
    job = db_tables.execute_query(select_query, (offerta_id,))
    if job:
        return jsonify(job)
    return jsonify({"message": "Offerta di lavoro non trovata"}), 404

@app.route('/jobs', methods=['GET'])
def get_jobs():
    """
    Restituisce la lista delle offerte di lavoro, ordinate per data di inserimento (decrescente),
    limitate al numero massimo indicato.
    """
    max_results = request.args.get('max_results', default=10, type=int)  # Numero massimo di risultati
    select_query = "SELECT * FROM jobs ORDER BY DataInserimento DESC LIMIT ?"
    
    jobs = db_tables.execute_query(select_query, (max_results,))
    if max_results < 0:
        return jsonify({"message": "Il numero massimo di risultati deve essere maggiore di 0"}), 400
    if jobs:
        return jsonify(jobs)
    else:
        print(f"jobs: {jobs}")
        print("Path database: ", db_path)
    return jsonify({"message": "Nessuna offerta di lavoro trovata"}), 404

import datetime

@app.route('/jobs', methods=['POST'])
def add_job():
    """
    Aggiunge una nuova offerta di lavoro.
    """
    data = request.get_json()
    
    # Parametri obbligatori
    titolo = data.get('Titolo')
    descrizione_breve = data.get('DescrizioneBreve')
    azienda = data.get('Azienda')
    provincia = data.get('Provincia')
    data_inserimento = data.get('DataInserimento')  # Data di inserimento nel formato 'YYYY-MM-DD'
    smart_working = data.get('SmartWorking')
    retribuzione_lorda = data.get('RetribuzioneLorda')
    tipologia_contratto = data.get('TipologiaContratto')

    # Controllo se tutti i campi obbligatori sono presenti
    if not all([titolo, descrizione_breve, azienda, provincia, data_inserimento, smart_working, retribuzione_lorda, tipologia_contratto]):
        return jsonify({"message": "Tutti i campi sono obbligatori"}), 400
    
    # Validazione della data
    try:
        data_inserimento = datetime.datetime.strptime(data_inserimento, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"message": "La data di inserimento deve essere nel formato 'YYYY-MM-DD'"}), 400

    # Validazione della retribuzione (deve essere un numero positivo)
    try:
        retribuzione_lorda = float(retribuzione_lorda)
        if retribuzione_lorda <= 0:
            return jsonify({"message": "La retribuzione lorda deve essere un numero positivo"}), 400
    except (ValueError, TypeError):
        return jsonify({"message": "La retribuzione lorda deve essere un numero valido"}), 400

    # Inserimento del job nel database
    try:
        db_tables.insert_job(titolo=titolo, descrizione_breve=descrizione_breve, azienda=azienda, provincia=provincia, data_inserimento=data_inserimento, smart_working=smart_working, retribuzione_lorda=retribuzione_lorda, tipologia_contratto=tipologia_contratto)
        return jsonify({"message": "Offerta di lavoro aggiunta con successo"}), 201
    except Exception as e:
        # Gestione errore generico in caso di fallimento dell'inserimento
        return jsonify({"message": f"Errore durante l'inserimento: {str(e)}"}), 500

from flask import jsonify, request

@app.route('/jobs/<int:offerta_id>', methods=['PUT'])
def update_job(offerta_id):
    """
    Modifica un'offerta di lavoro esistente.
    """
    try:
        # Recupero dei dati dal corpo della richiesta
        data = request.get_json()

        # Verifica se i dati sono validi
        if not data:
            return jsonify({"error": "Dati non validi. Assicurati che il corpo della richiesta sia in formato JSON."}), 400

        # Parametri da aggiornare
        titolo = data.get('Titolo')
        descrizione_breve = data.get('DescrizioneBreve')
        azienda = data.get('Azienda')
        provincia = data.get('Provincia')
        smart_working = data.get('SmartWorking')
        retribuzione_lorda = data.get('RetribuzioneLorda')
        tipologia_contratto = data.get('TipologiaContratto')

        # Verifica se l'offerta di lavoro esiste nel database
        check_query = "SELECT 1 FROM jobs WHERE OffertaLavoroID = ?"
        result = db_tables.execute_query(check_query, (offerta_id,))

        if not result:
            return jsonify({"error": f"L'offerta di lavoro con ID {offerta_id} non esiste."}), 404

        # Costruzione dinamica della query di aggiornamento
        set_clause = []
        params = []

        # Aggiungi solo i parametri che sono stati forniti
        if titolo:
            set_clause.append("Titolo = ?")
            params.append(titolo)
        if descrizione_breve:
            set_clause.append("DescrizioneBreve = ?")
            params.append(descrizione_breve)
        if azienda:
            set_clause.append("Azienda = ?")
            params.append(azienda)
        if provincia:
            set_clause.append("Provincia = ?")
            params.append(provincia)
        if smart_working is not None:  # Gestiamo anche i valori booleani
            set_clause.append("SmartWorking = ?")
            params.append(smart_working)
        if retribuzione_lorda is not None:
            set_clause.append("RetribuzioneLorda = ?")
            params.append(retribuzione_lorda)
        if tipologia_contratto:
            set_clause.append("TipologiaContratto = ?")
            params.append(tipologia_contratto)

        # Se non ci sono campi da aggiornare, ritorniamo un errore
        if not set_clause:
            return jsonify({"error": "Nessun campo da aggiornare."}), 400

        # Aggiungi l'ID dell'offerta alla fine dei parametri per la query
        params.append(offerta_id)

        # Costruzione della query finale
        update_query = f"""
        UPDATE jobs
        SET {', '.join(set_clause)}
        WHERE OffertaLavoroID = ?
        """

        # Esegui la query di aggiornamento
        db_tables.execute_query(update_query, tuple(params))

        return jsonify({"message": f"Offerta di lavoro {offerta_id} aggiornata con successo."}), 200

    except Exception as e:
        # In caso di errore imprevisto, restituisci un errore generico
        return jsonify({"error": f"Si è verificato un errore durante l'aggiornamento dell'offerta di lavoro: {str(e)}"}), 500

@app.route('/jobs/<int:offerta_id>', methods=['DELETE'])
def delete_job(offerta_id):
    """
    Elimina un'offerta di lavoro esistente.
    """
    delete_query = "DELETE FROM jobs WHERE OffertaLavoroID = ?"
    db_tables.execute_query(delete_query, (offerta_id,))
    return jsonify({"message": f"Offerta di lavoro {offerta_id} eliminata con successo"}), 200

@app.route('/jobs/search', methods=['GET'])
def search_jobs():
    """
    Restituisce la lista delle offerte di lavoro che contengono un determinato testo nel Titolo o nella DescrizioneBreve.
    """
    search_text = request.args.get('search_text', default='', type=str)
    max_results = request.args.get('max_results', default=10, type=int)
    
    search_query = """
    SELECT * FROM jobs
    WHERE Titolo LIKE ? OR DescrizioneBreve LIKE ?
    ORDER BY DataInserimento DESC
    LIMIT ?
    """
    # Esegui la ricerca
    jobs = db_tables.execute_query(search_query, ('%' + search_text + '%', '%' + search_text + '%', max_results))
    if jobs:
        return jsonify(jobs)
    return []
    #return jsonify({"message": "Nessuna offerta di lavoro trovata per la ricerca"}), 404

@app.route('/jobs/search-all', methods=['GET'])
def search_jobs_by_all_paramethers():
    """
    Restituisce la lista delle offerte di lavoro che contengono un determinato testo nei parametri specificati.
    Se non vengono passati parametri, la ricerca è "normale" (tutti i parametri sono considerati).
    """
    try:
        # Recupero dei parametri di ricerca dalla richiesta
        search_text = request.args.get('search_text', default='', type=str)
        max_results = request.args.get('max_results', default=10, type=int)
        titolo = request.args.get('Titolo', default=None, type=str)
        descrizione_breve = request.args.get('DescrizioneBreve', default=None, type=str)
        azienda = request.args.get('Azienda', default=None, type=str)
        provincia = request.args.get('Provincia', default=None, type=str)
        smart_working = request.args.get('SmartWorking', default=None, type=str)
        retribuzione_lorda = request.args.get('RetribuzioneLorda', default=None, type=float)
        tipologia_contratto = request.args.get('TipologiaContratto', default=None, type=str)
        data_inserimento = request.args.get('DataInserimento', default=None, type=str)  # Formato 'YYYY-MM-DD'

        # Costruzione della query dinamica
        query_conditions = []
        query_params = []

        # Aggiungi condizioni per ogni parametro che è stato fornito
        if titolo:
            query_conditions.append("Titolo LIKE ?")
            query_params.append('%' + titolo + '%')
        if descrizione_breve:
            query_conditions.append("DescrizioneBreve LIKE ?")
            query_params.append('%' + descrizione_breve + '%')
        if azienda:
            query_conditions.append("Azienda LIKE ?")
            query_params.append('%' + azienda + '%')
        if provincia:
            query_conditions.append("Provincia LIKE ?")
            query_params.append('%' + provincia + '%')
        if smart_working is not None:
            query_conditions.append("SmartWorking = ?")
            query_params.append(smart_working)
        if retribuzione_lorda is not None:
            query_conditions.append("RetribuzioneLorda = ?")
            query_params.append(retribuzione_lorda)
        if tipologia_contratto:
            query_conditions.append("TipologiaContratto LIKE ?")
            query_params.append('%' + tipologia_contratto + '%')
        if data_inserimento:
            query_conditions.append("DataInserimento = ?")
            query_params.append(data_inserimento)

        # Se non ci sono parametri di ricerca, facciamo una ricerca "normale" (titolo o descrizione breve)
        if not query_conditions:
            query_conditions.append("(Titolo LIKE ? OR DescrizioneBreve LIKE ?)")
            query_params.extend(['%' + search_text + '%', '%' + search_text + '%'])

        # Se ci sono condizioni, aggiungi la parte WHERE
        where_clause = " AND ".join(query_conditions)
        
        # Aggiungi la condizione di ordinamento e limite
        search_query = f"SELECT * FROM jobs WHERE {where_clause} ORDER BY DataInserimento DESC LIMIT ?"
        query_params.append(max_results)

        # Esegui la query di ricerca
        jobs = db_tables.execute_query(search_query, tuple(query_params))

        if jobs:
            return jsonify(jobs)
        else:
            return jsonify({"message": "Nessuna offerta di lavoro trovata per la ricerca."}), 404

    except Exception as e:
        # Gestione degli errori
        return jsonify({"error": f"Si è verificato un errore durante la ricerca: {str(e)}"}), 500
    #return jsonify({"message": "Nessuna offerta di lavoro trovata per la ricerca"}), 404

if __name__ == '__main__':
    app.run(debug=True)