import json
import sqlite3

# Charger le fichier JSON
with open("./clues_full.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Connexion à la base de données SQLite (ou création)
conn = sqlite3.connect("database.sqlite")
cursor = conn.cursor()

# Création de la table
cursor.execute("""
CREATE TABLE IF NOT EXISTS clues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    posX INTEGER,
    posY INTEGER,
    name_fr TEXT
)
""")

# Extraction et insertion des données
for map_id, map_data in data["maps"].items():
    posX = map_data["position"]["x"]
    posY = map_data["position"]["y"]

    for clue_id in map_data["clues"]:
        # Recherche du clue dans la liste "clues"
        clue = next((c for c in data["clues"] if c["clue-id"] == clue_id), None)
        if clue:
            name_fr = clue["name-fr"]
            # Insertion dans la base de données
            cursor.execute("INSERT INTO clues (posX, posY, name_fr) VALUES (?, ?, ?)", (posX, posY, name_fr))

# Sauvegarde des changements et fermeture
conn.commit()
conn.close()

print("Les données ont été importées avec succès dans la base de données.")
