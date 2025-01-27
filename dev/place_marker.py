import json
from pynput.mouse import Listener

# Chemin vers le fichier de configuration où les coordonnées seront stockées
config_file = 'dev/mouse_position_config.json'

# Fonction pour enregistrer les coordonnées dans un fichier JSON
def save_coordinates(x, y):
    x = x - 132
    y = y - 10
    config = {"x": x, "y": y}
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=4)
    print(f"Les coordonnées ont été enregistrées : x={x}, y={y}")
    print("Les coordonnées ont été sauvegardées dans 'mouse_position_config.json'.")

# Fonction pour écouter les clics de souris et récupérer la position
def on_click(x, y, button, pressed):
    if pressed:
        print(f"Clic détecté aux coordonnées : ({x}, {y})")
        save_coordinates(x, y)
        # Arrêter l'écoute après le premier clic
        return False

def start():
    # Demander à l'utilisateur de cliquer pour enregistrer la position
    print("\n")
    print("Clique dans le rond noir du premier marqueur blanc de la chasse pour enregistrer les coordonées du marqueur.")
    print("\n")
    print("Pensez à redecocher le marqueur après")

    # Écouteur pour capter les clics de souris
    with Listener(on_click=on_click) as listener:
        listener.join()


def load_coordinates():
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
            x = config.get("x")
            y = config.get("y")
            if x is not None and y is not None:
                print(f"Coordonnées récupérées : x={x}, y={y}")
                return x, y
            else:
                print("Les coordonnées n'ont pas été trouvées dans le fichier.")
                return None, None
    except FileNotFoundError:
        print(f"Le fichier {config_file} n'a pas été trouvé.")
        return None, None
    

if __name__ == "__main__":
    start()
    #valider(132, 124)
    #move(262,286)