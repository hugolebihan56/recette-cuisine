import asyncio
import hashlib
import json
import multiprocessing
import os
import cv2
import requests
from autoclicker import  click_position_right, hold_key_while_capturing, write_in_chat, click_position
from utils import change_map
from screenshot import capture_and_crop, capture_full_window, capture_full_window_datetime
from text_extractor import extract_text, extract_coo, extract_indice, count_indices
from api_client import call_bdd, get_pos_next_indice
import pyperclip
import time
from logger_config import logger, archimonstre_logger
import bot as discordBot

LOCAL_DB_PATH = "merged_database_v2.db"
REMOTE_DB_URL = "https://raw.githubusercontent.com/hugolebihan56/recette-cuisine/refs/heads/main/merged_database_v2.db"

previous_coo_actual = []



class TimeoutException(Exception):
    """Exception personnalisée pour le timeout."""
    pass


def calculate_file_hash(file_path):
    """
    Calcule le hash SHA-256 d'un fichier local.
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def fetch_remote_file_hash(url):
    """
    Récupère le hash SHA-256 d'un fichier en ligne sans le télécharger complètement.
    """
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    sha256_hash = hashlib.sha256()
    for byte_block in response.iter_content(chunk_size=4096):
        sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def update_local_database():
    """
    Vérifie si la base de données locale est à jour par rapport à la version en ligne,
    et met à jour la version locale si nécessaire.
    """
    if not os.path.exists(LOCAL_DB_PATH):
        logger.info("La base de données locale n'existe pas. Téléchargement de la version en ligne...")
        download_remote_database()
        return

    # Calcul des hash locaux et distants
    # logger.info("Calcul du hash de la base de données locale...")
    local_hash = calculate_file_hash(LOCAL_DB_PATH)
    #logger.info(f"Hash local : {local_hash}")

    #logger.info("Calcul du hash de la base de données en ligne...")
    remote_hash = fetch_remote_file_hash(REMOTE_DB_URL)
    #logger.info(f"Hash distant : {remote_hash}")

    # Comparaison des hash
    if local_hash != remote_hash:
        logger.info("La base de données locale est obsolète. Téléchargement de la version en ligne...")
        download_remote_database()
    else:
        logger.info("La base de données locale est à jour.")

def download_remote_database():
    """
    Télécharge la base de données en ligne et remplace la version locale.
    """
    response = requests.get(REMOTE_DB_URL)
    response.raise_for_status()

    with open(LOCAL_DB_PATH, "wb") as f:
        f.write(response.content)
    logger.info(f"Base de données mise à jour avec succès : {LOCAL_DB_PATH}")


def target(func, result_queue, *args, **kwargs):
    """
    Fonction cible exécutée dans un processus séparé.
    Utilisée pour appeler la fonction cible et mettre son résultat dans une queue.
    """
    try:
        result_queue.put(func(*args, **kwargs))
    except Exception as e:
        result_queue.put(e)

def execute_with_timeout(func, timeout, *args, **kwargs):
    """
    Exécute une fonction avec un délai maximum dans un processus distinct.
    Si la fonction dépasse ce délai, elle est interrompue et une exception TimeoutException est levée.
    """
    result = multiprocessing.Queue()
    process = multiprocessing.Process(target=target, args=(func, result, *args), kwargs=kwargs)
    process.start()

    start_time = time.time()
    last_print_time = start_time  # Initialisation pour gérer l'affichage

    while process.is_alive():
        elapsed_time = time.time() - start_time

        # Afficher le temps écoulé toutes les minutes
        if elapsed_time - (last_print_time  - start_time) >= 60:
            logger.info(f"Temps écoulé : {elapsed_time // 60:.0f} minute(s) et {elapsed_time % 60:.0f} seconde(s)")
            last_print_time  = time.time()

        if elapsed_time > timeout:
            logger.info(f"Temps limite de {timeout} secondes atteint. Arrêt de la fonction.")
            process.terminate()
            process.join()
            raise TimeoutException(f"La fonction {func.__name__} a dépassé le temps limite de {timeout} secondes.")

        time.sleep(1)  # Pause courte pour maintenir la réactivité

    process.join()  # S'assurer que le processus est bien terminé

    if not result.empty():
        output = result.get()
        if isinstance(output, Exception):
            raise output  # Relève l'exception si une erreur est survenue dans la fonction
        return output
    return None


def main():

    logger.info("Vérification de la base de données.")
    update_local_database()

    os.makedirs("screen", exist_ok=True) 

    region = (10, 265, 275, 750) # Indices
    
    # Chemin pour sauvegarder l'image
    save_path = os.path.join("screen", "screen_zone.png")
    
    nombre_etape = 4 #La dernière étape c'est le coffre

    for etape in range(1, nombre_etape):
        logger.info(f"Lancement de l'étape : {etape} / {nombre_etape}")

        capture_and_crop(region, save_path)

        try:
            execute_with_timeout(do_etape, 270, region, save_path)  # Timeout de 6 minutes
        except TimeoutException as e:
            logger.info(e)
            logger.info(f"Interruption de l'étape {etape} après 15 minutes.")
            raise Exception(f"Interruption de l'étape {etape} après 6 minutes.")
        except Exception as e:
            raise Exception(f"Erreur inattendue lors de l'étape {etape} : {e}")


def get_coo_actual():
    region_coo_actual = (5, 70, 100, 95)
    save_path_coo_actual = os.path.join("screen", "coo_actual.png")
    capture_and_crop(region_coo_actual, save_path_coo_actual)
    return extract_coo(extract_text(save_path_coo_actual, coo=True), save_path_coo_actual)

def get_target_coords_and_width(target, rigeur, log=True):
    # Charger le screenshot et l'image cible
    screenshot = cv2.imread('screen/screen_global.png', cv2.IMREAD_COLOR)
    template = cv2.imread(f'screen/{target}.png', cv2.IMREAD_COLOR)

    # Obtenir les dimensions de l'image cible
    h, w, _ = template.shape

    # Appliquer la méthode de template matching
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)

    # Trouver la meilleure correspondance
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    # Vérifier si la correspondance est au-dessus d'un seuil
    if max_val >= rigeur:
        # Coordonnées du coin supérieur gauche
        top_left = max_loc

        # Calculer les coordonnées du centre
        center_x = top_left[0] + w // 2
        center_y = top_left[1] + (h // 2)


        # Dessiner le rectangle autour de la meilleure correspondance
        cv2.rectangle(screenshot, top_left, (top_left[0] + w, top_left[1] + h), (0, 255, 0), 2)

        # Dessiner le point rouge au centre
        cv2.circle(screenshot, (center_x, center_y), 5, (0, 0, 255), -1)

        # Afficher les coordonnées dans la console
        
        #logger.info(f"Point rouge détecté aux coordonnées : (x={center_x}, y={center_y})")
        
        # Afficher le résultat
        # cv2.imshow('Detected', screenshot)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        return center_x, center_y, top_left[0] + w
    else:
        if log:
            logger.error(f"Aucune correspondance trouvée pour [{target}] avec un score suffisant.")
        return None, None, None

def get_target_coords(target, rigeur, log=True):
    # Charger le screenshot et l'image cible
    screenshot = cv2.imread('screen/screen_global.png', cv2.IMREAD_COLOR)
    template = cv2.imread(f'screen/{target}.png', cv2.IMREAD_COLOR)

    # Obtenir les dimensions de l'image cible
    h, w, _ = template.shape

    # Appliquer la méthode de template matching
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)

    # Trouver la meilleure correspondance
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    # Vérifier si la correspondance est au-dessus d'un seuil
    if max_val >= rigeur:
        # Coordonnées du coin supérieur gauche
        top_left = max_loc

        # Calculer les coordonnées du centre
        center_x = top_left[0] + w // 2
        center_y = top_left[1] + h // 2


        # Dessiner le rectangle autour de la meilleure correspondance
        cv2.rectangle(screenshot, top_left, (top_left[0] + w, top_left[1] + h), (0, 255, 0), 2)

        # Dessiner le point rouge au centre
        cv2.circle(screenshot, (center_x, center_y), 5, (0, 0, 255), -1)

        # Afficher les coordonnées dans la console
        
        #logger.info(f"Point rouge détecté aux coordonnées : (x={center_x}, y={center_y})")
        
        # # Afficher le résultat
        # cv2.imshow('Detected', screenshot)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        return center_x, center_y

    else:
        if log:
            logger.error(f"Aucune correspondance trouvée pour [{target}] avec un score suffisant.")
        return None, None

def sortir_du_trou():
    time.sleep(5)
    capture_full_window()
    x, y = get_target_coords("trou_1k", 0.8)
    click_position(x, y, True)
    time.sleep(5)

    capture_full_window()
    x, y = get_target_coords("echelle_trou", 0.7)
    click_position(x, y, True)
    time.sleep(6)


def find_archimonstre(extracted_coo_actual, previous_coo):
    capture_full_window()
    _x, _y = get_target_coords("archimonstre", 0.7, False)
    if _x != None:
        path  = capture_full_window_datetime()
        archimonstre_logger.info(f"Archimonstre trouvé : coordonées={extracted_coo_actual}, coordonées précédentes={previous_coo}")
        discordBot.image_path = path
        discordBot.message = f"@everyone Archimonstre trouvé : coordonées={extracted_coo_actual}, coordonées précédentes={previous_coo}"
        if previous_coo != extracted_coo_actual:
            try:
                asyncio.run(discordBot.BotRun())
            except:
                logger.error('Erreur lors de l envoi discord')


def do_etape(region, save_path):
    num_indices = count_indices(save_path)
    logger.info(f"Nombre d'indices détectés : {num_indices}")

    # Extraction de texte
    for indice in range(1, num_indices + 1):

        logger.info(f"On passe à l'indice : {indice} / {num_indices}")

        capture_and_crop(region, save_path)

        arrow_direction, extracted_text, marker_coo = extract_indice(save_path, indice)

        extracted_coo_actual = get_coo_actual()

        if extracted_text:
            logger.info(f"Texte extrait : {arrow_direction} - {extracted_text}")

            logger.info(f"Coordonnées actuelle : {extracted_coo_actual}")

            if extracted_coo_actual != None:
                x = extracted_coo_actual[0]
                y = extracted_coo_actual[1]
            else:
                global previous_coo_actual
                if not previous_coo_actual:
                    previous_coo_actual = [int(input("x = ")), int(input("y = "))]
                x = previous_coo_actual[0]
                y = previous_coo_actual[1]
                extracted_coo_actual = (x, y)

            direction = arrow_direction

            # Appeler l'API
            #api_response = send_treasure_hunt_request(x, y, direction)
            response_json = call_bdd(x, y, direction)
            api_response = json.loads(response_json)
            #logger.info(api_response)

            if api_response or  "Phorreur" in extracted_text:

                x, y = get_pos_next_indice(api_response, extracted_text, extracted_coo_actual)
                if x is None and y is None:
                    # Passer à l'indice suivant
                    
                    x_cherche, y_cherche = find_phorreur(extracted_coo_actual, direction, extracted_text)

                    logger.info(f"Map de l'indice {x_cherche, y_cherche}")

                    previous_coo_actual = (x_cherche, y_cherche )

                    click_position(marker_coo[0], marker_coo[1])
                    time.sleep(1)    
                                    # Si on arrive au dernier indice trouvé on change d'étape ! 
                    if indice == num_indices:
                        logger.info("Fin d'une étape, on va passer à la suivante !")
                        click_position(marker_coo[0], marker_coo[1] + 36)
                        time.sleep(1)
                        
                    continue

                travel_command = f"/travel {x} {y}"
                pyperclip.copy(travel_command)  # Copie la commande dans le presse-papier
                logger.info(f"Commande copiée dans le presse-papier : {travel_command}")
                write_in_chat()

                compteur_none = 0
                compeur_bloque = 0
                previous_coo = []

                    # Comparer les coordonnées actuelles avec celles de l'API
                while not compare_coordinates(extracted_coo_actual, [x, y]):

                    time.sleep(1)
                    extracted_coo_actual = get_coo_actual()

                    find_archimonstre(extracted_coo_actual, previous_coo)

                    if extracted_coo_actual == None:
                        compteur_none += 1
                    
                    else : 
                        compteur_none = 0
                        #logger.info(f"Attendre la fin du voyage : {extracted_coo_actual} -> ({x}, {y}) 🏃")

                        if extracted_coo_actual[0] == 6 and extracted_coo_actual[1] == 13 and previous_coo[0] == 6 and previous_coo[1] == 13:
                            #sortir_du_trou()
                            time.sleep(1)

                            if direction == '0':
                                pyperclip.copy("/travel 7 12")
                                write_in_chat()
                                time.sleep(15)
                            
                            pyperclip.copy(travel_command)
                            write_in_chat()
                            time.sleep(4)
                    

                    if extracted_coo_actual != None and (extracted_coo_actual == previous_coo):
                        compeur_bloque += 1
                        
                        if extracted_coo_actual[0] == -17 and extracted_coo_actual[1] == 8:
                            time.sleep(3)
                            change_map("haut")
                            raise Exception('Canyon sauvage !!! ')
                    
                    else : 
                        compeur_bloque = 0

                    if compeur_bloque >= 7:
                        logger.error("Bloqué sur une map (dalle, autre) changement manuel")
                        if direction == '0':
                            change_map("droite")
                        elif direction == '2':
                            change_map("bas")
                        elif direction == '4':
                            change_map("gauche")
                        elif direction == '6':
                            change_map("haut")

                        time.sleep(5)
                        compeur_bloque = 0
                        pyperclip.copy(travel_command)
                        write_in_chat()


                    if compteur_none >= 12:
                        logger.info(f"Attendre la fin du voyage : ({x}, {y}) -> ({x}, {y}) 🏃")
                        logger.error(f"Aucune coordonées, on estime que l'on est arrivé !")
                        extracted_coo_actual = (x,y)
                        
                    previous_coo = extracted_coo_actual
                    # Mettre à jour les coordonnées précédentes
                    previous_coo_actual = extracted_coo_actual

                
                logger.info(f"Map de l'indice {x, y}")

                click_position(marker_coo[0], marker_coo[1])
                time.sleep(1)
                # Si on arrive au dernier indice trouvé on change d'étape ! 
                if indice == num_indices:
                    logger.info("Fin d'une étape, on va passer à la suivante !")
                    click_position(marker_coo[0], marker_coo[1] + 36)
                    time.sleep(1)
            else:
                logger.error("Erreur : Impossible de récupérer les données de l'API.")
        else:
            logger.error("Aucun texte trouvé dans l'image.")


def find_phorreur(extracted_coo_actual, direction, extracted_text):

    phorreur_trouve = False
    x_cherche = extracted_coo_actual[0]
    y_cherche = extracted_coo_actual[1]
    while not phorreur_trouve:
        if direction == '0':
            x_cherche = x_cherche + 1
        elif direction == '4':
            x_cherche = x_cherche - 1
        elif direction == '6':
            y_cherche = y_cherche - 1
        elif direction == '2':
            y_cherche = y_cherche + 1

        travel_command = f"/travel {x_cherche} {y_cherche}"
        pyperclip.copy(travel_command)  # Copie la commande dans le presse-papier
        #logger.info(f"Commande copiée dans le presse-papier : {travel_command}")
        write_in_chat()    
        time.sleep(1)
        extracted_coo_actual = get_coo_actual()
        while not compare_coordinates(extracted_coo_actual, [x_cherche, y_cherche]):
            #logger.info("On se déplace pour trouver le phorreur")
            time.sleep(1)
            extracted_coo_actual = get_coo_actual()

        click_position_right(50, 500)
        hold_key_while_capturing("z", 'screen/screen_global.png')
        logger.info(f"On cherche un phorreur : {extracted_text}")
        if "baveux" in extracted_text:
            x, _ = get_target_coords("baveux", 0.8)
            if x == None:
                phorreur_trouve =  False
            else:
                phorreur_trouve =  True
        elif "chafouin" in extracted_text:
            x, _ = get_target_coords("chafouin", 0.8)
            if x == None:
                phorreur_trouve =  False
            else:
                phorreur_trouve =  True
        elif "sournois" in extracted_text or "sourncis" in extracted_text:
            x, _ = get_target_coords("sournois", 0.8)
            if x == None:
                phorreur_trouve =  False
            else:
                phorreur_trouve =  True
        elif "fourbe" in extracted_text:
            x, _ = get_target_coords("fourbe", 0.8)
            if x == None:
                phorreur_trouve =  False
            else:
                phorreur_trouve =  True
        else:
            x, _ = get_target_coords("phorreur", 0.8)
            if x == None:
                phorreur_trouve =  False
            else:
                phorreur_trouve =  True

    return x_cherche, y_cherche
    
    
def compare_coordinates(coo1, coo2):
    """
    Compare deux coordonnées sous forme de listes.
    Vérifie que les coordonnées sont exactement égales en termes d'entiers,
    en éliminant les problèmes de type et d'espaces.
    """
    try:
        # Convertir les coordonnées en entiers, au cas où elles seraient flottantes ou sous forme de chaîne
        coo1 = [int(coord) for coord in coo1]
        coo2 = [int(coord) for coord in coo2]
        
        # Comparer les coordonnées
        return coo1 == coo2
    except (ValueError, TypeError) as e:
        # Si une erreur se produit (par exemple une conversion impossible), afficher l'erreur et continuer
        #logger.info(f"Erreur lors de la comparaison des coordonnées : {e}")
        return False

    
if __name__ == "__main__":
    #find_archimonstre((0,0), (0,0))
    main()
