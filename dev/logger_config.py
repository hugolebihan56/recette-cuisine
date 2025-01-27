from datetime import datetime
import logging

today_date = datetime.now().strftime("%Y-%m-%d")  

# Configure the logger
logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)

# Create a formatter to define the log format
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Create a file handler to write logs to a file with UTF-8 encoding
file_handler = logging.FileHandler(f'Today/app_{today_date}.log', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

# Create a stream handler to print logs to the console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# Add the handlers to the logger (only once to avoid duplicates)
if not logger.hasHandlers():  # Prevent adding handlers multiple times
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

 
archimonstre_logger = logging.getLogger("ArchimonstreLogger")
archimonstre_logger.setLevel(logging.INFO)

# Création d'un gestionnaire de fichier pour ce logger
file_handler = logging.FileHandler(f"Today/archimonstre_log_{today_date}.txt",encoding='utf-8')
file_handler.setLevel(logging.INFO)

# Format pour les logs du fichier spécifique
formatter = logging.Formatter("%(asctime)s - %(message)s")
file_handler.setFormatter(formatter)

# Ajout du gestionnaire de fichier au logger dédié
archimonstre_logger.addHandler(file_handler)
