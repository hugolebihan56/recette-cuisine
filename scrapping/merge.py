import sqlite3
import glob
import os

def remove_duplicates(db_path):
    """
    Supprime les doublons dans la table 'points_of_interest' en gardant uniquement les lignes uniques.
    
    Args:
        db_path (str): Chemin vers la base de données SQLite.
    """
    # Connexion à la base de données
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Créer une table temporaire avec les données uniques
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS temp_table AS
    SELECT MIN(id) AS id, posX, posY, name_fr
    FROM points_of_interest
    GROUP BY posX, posY, name_fr;
    """)

    # Supprimer toutes les lignes de la table principale
    cursor.execute("DELETE FROM points_of_interest;")

    # Réinsérer les données uniques depuis la table temporaire
    cursor.execute("""
    INSERT INTO points_of_interest (id, posX, posY, name_fr)
    SELECT id, posX, posY, name_fr
    FROM temp_table;
    """)

    # Supprimer la table temporaire
    cursor.execute("DROP TABLE temp_table;")

    # Sauvegarder les changements et fermer la connexion
    conn.commit()
    conn.close()

    print("Les doublons ont été supprimés avec succès.")



def merge_databases(source_paths, target_path):
    """
    Fusionne plusieurs bases SQLite en une seule.
    
    Args:
        source_paths (list): Liste des chemins des bases source.
        target_path (str): Chemin de la base cible.
    """
    import sqlite3

    # Connecter à la base cible
    target_conn = sqlite3.connect(target_path)
    target_cursor = target_conn.cursor()

    # Créer la structure de la table dans la base cible si nécessaire
    create_table_query = """
    CREATE TABLE IF NOT EXISTS points_of_interest (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        posX INTEGER,
        posY INTEGER,
        name_fr TEXT
    );
    """
    target_cursor.execute(create_table_query)

    # Parcourir chaque base source
    for source_path in source_paths:
        print(f"Fusion de la base : {source_path}")

        # Connecter à la base source
        source_conn = sqlite3.connect(source_path)
        source_cursor = source_conn.cursor()

        # Vérifier si la colonne 'id' existe dans la table source
        source_cursor.execute("PRAGMA table_info(points_of_interest);")
        columns = [col[1] for col in source_cursor.fetchall()]

        # Ajuster la requête d'insertion en fonction des colonnes
        if 'id' in columns:
            rows = source_cursor.execute("SELECT id, posX, posY, name_fr FROM points_of_interest").fetchall()
            for row in rows:
                target_cursor.execute(
                    "INSERT OR IGNORE INTO points_of_interest (id, posX, posY, name_fr) VALUES (?, ?, ?, ?)",
                    row
                )
        else:
            rows = source_cursor.execute("SELECT posX, posY, name_fr FROM points_of_interest").fetchall()
            for row in rows:
                target_cursor.execute(
                    "INSERT INTO points_of_interest (posX, posY, name_fr) VALUES (?, ?, ?)",
                    row
                )

        # Fermer la connexion à la base source
        source_conn.close()

    # Valider les changements dans la base cible
    target_conn.commit()
    target_conn.close()
    print(f"Fusion terminée. Les données sont dans : {target_path}")


# # Exemple d'utilisation
# db_folder = os.path.join(os.path.dirname(__file__), "db")
# source_files = glob.glob(os.path.join(db_folder, "*.db"))
# print("Bases de données trouvées :", source_files)

# target_file = "merged_database_v3.db"  # Chemin vers la base cible

# merge_databases(source_files, target_file)

# Exemple d'utilisation
database_path = "./merged_database_v3.db"  # Remplacez par le chemin de votre base
remove_duplicates(database_path)