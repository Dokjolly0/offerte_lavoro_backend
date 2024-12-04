import os
import sys

class DBConfig:
    """Classe per gestire i parametri di configurazione del database."""
    def __init__(self, path=".", name="job_offert.db"):
        if not os.path.isdir(path):
            print("Il percorso specificato non esiste.")
            return
        if not name.endswith(".db"):
            print("Il nome del database deve terminare con '.db'.")
            return
        self.path = path
        self.name = name

    @property
    def full_path(self):
        """Restituisce il percorso completo del file del database."""
        return os.path.join(self.path, self.name)