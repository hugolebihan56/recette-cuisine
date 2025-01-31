import base64
import requests

# Informations sur votre dépôt et fichier
GITHUB_REPO = "hugolebihan56/recette-cuisine"  # Nom du dépôt (utilisateur/nom_du_dépôt)
FILE_PATH = "merged_database_v2.db"           # Chemin du fichier dans le dépôt
GITHUB_TOKEN = ""   # Remplacez par votre token personnel

def get_file_sha(repo, file_path, token):
    """
    Récupère le SHA du fichier existant sur GitHub.
    Le SHA est nécessaire pour effectuer une mise à jour via l'API GitHub.
    """
    url = f"https://api.github.com/repos/{repo}/contents/{file_path}"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    file_info = response.json()
    return file_info["sha"]

def update_github_file(repo, file_path, local_file_path, token, commit_message):
    """
    Met à jour un fichier sur GitHub avec le contenu d'un fichier local.
    """
    # Récupère le contenu local
    with open(local_file_path, "rb") as f:
        content = f.read()
    encoded_content = base64.b64encode(content).decode("utf-8")

    # Récupère le SHA du fichier existant
    file_sha = get_file_sha(repo, file_path, token)

    # Prépare la requête de mise à jour
    url = f"https://api.github.com/repos/{repo}/contents/{file_path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "message": commit_message,
        "content": encoded_content,
        "sha": file_sha
    }

    response = requests.put(url, json=payload, headers=headers)

    if response.status_code == 200 or response.status_code == 201:
        print(f"Fichier {file_path} mis à jour avec succès sur GitHub.")
    else:
        print(f"Erreur lors de la mise à jour du fichier : {response.status_code}")
        print(response.json())

def maj_bdd():
    LOCAL_FILE_PATH = "merged_database_v2.db"

    update_github_file(
        GITHUB_REPO,
        FILE_PATH,
        LOCAL_FILE_PATH,
        GITHUB_TOKEN,
        commit_message="Mise à jour de la base de données"
    )


if __name__ == "__main__":
    # Chemin de votre fichier local à uploader
    LOCAL_FILE_PATH = "merged_database_v2.db"

    update_github_file(
        GITHUB_REPO,
        FILE_PATH,
        LOCAL_FILE_PATH,
        GITHUB_TOKEN,
        commit_message="Mise à jour de la base de données "
    )
