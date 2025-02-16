import logging
import os
import time
import keyboard
import numpy as np
import pyperclip

from autoclicker import click_position, click_position_right, ctrl_click, double_click_position, go_down, go_left, go_right, go_up, hold_key_while_capturing, move_mouse_smoothly, write_in_chat
from api_client import get_id_of_map, get_name_area_from_id, get_zaap_from_map
from utils import change_map
from main import compare_coordinates, get_coo_actual, get_target_coords, get_target_coords_and_width, main
from text_extractor import extract_coo, extract_text
from screenshot import capture_and_crop, capture_bottom_left_corner, capture_bottom_right_corner, capture_full_window
from config import Resolution
from logger_config import logger

LOG_FILE = "log_exceptions.txt"
logger = logging.getLogger('my_logger')

def find_door():
    logger.info("🚪")
    time.sleep(1)
    capture_full_window()
    door = "door"
    if Resolution == "1k":
        door = "door_1k"
    return get_target_coords(door, 0.8)


def take_door():
    compteur_fail = 0
    time.sleep(1)
    while True:
        x,y = find_door()
        if x != None:
            compteur_fail = 0
            logger.info("🚪 ✅")
            click_position(x, y)
            time.sleep(8)
            break
        else :
            compteur_fail += 1
            logger.error("🚪 ❌")

        if compteur_fail >= 10:
            logger.error("🚪 ❌ x10 on va revenir depuis le zaap")
            go_havre_sac()
            open_zaap()
            go_cania()




def take_sun():
    logger.info("☀️")
    capture_full_window()
    # Des connards qui restent devant le truc
    sun = "sun"
    if Resolution == "1k":
        sun = "sun_1k"
    x, y = get_target_coords(sun, 0.7)
    if x != None:
        click_position(x, y)
        logger.info("☀️ ✅")
        time.sleep(6)
    else:
        logger.info("☀️ ❌")
        x, y = get_target_coords("sun2", 0.7)
        if x != None:
            click_position(x, y)
            logger.info("☀️ ✅")
            time.sleep(6)
        else:
            # Ce jeu de merde charge pas tout, on sort et re rentre
            logger.info("☀️ ❌")
            quit_malle()
            take_door()
            take_sun()


def take_combat():
    logger.info("🤺")
    capture_full_window()
    x, y = get_target_coords("combat", 0.8)
    click_position(x, y, True)
    time.sleep(4)

def take_challs():
    logger.info("💪")
    capture_full_window()
    x, y = get_target_coords("chall", 0.6)
    if x != None:
        click_position(x, y, True)
        time.sleep(1.5)
        return True
    else : 
        time.sleep(46)
        return False

    

def set_ready():
    logger.info("✅")
    capture_full_window()
    x, y = get_target_coords("pret", 0.8)
    if x != None:
        click_position(x, y,True)
        time.sleep(3)
    else : 
        time.sleep(58)

def get_sort():
    logger.info("🪄")
    capture_full_window()
    x, y = get_target_coords("roullage", 0.8)
    time.sleep(1)
    return x,y

def send_sort():
    logger.info("✨")
    capture_full_window()
    x, y = get_target_coords("coffre", 0.8)
    if x != None:
        click_position(x, y, True)
    else:
        # Pas de mimic (bug dofus)
        x, y = get_target_coords("coffre_ferme", 0.8)
        if x != None:
            click_position(x, y, True)

def end_turn():
    capture_full_window()
    x, y = get_target_coords("end", 0.8)
    if x == None:
        #Ca doit etre les chiffres, 5 4 3 2 1 . On attend 5 secondes ducoup
        time.sleep(6)
    else : 
        click_position(x, y, True)

def combat_fini():
    capture_full_window()
    x, y = get_target_coords("malle", 0.70)
    if x == None:
        logger.info("Le combat est fini")
        return True
    return False


def combat():
    take_combat()
    chall_pris = take_challs()
    if chall_pris:
        set_ready()
    x, y = get_sort()
    finito = False
    while not finito:
        for _ in range(3):
            finito = combat_fini()
            if finito:  # Quitter immédiatement 
                break
            time.sleep(1)
            click_position(x, y, True)
            send_sort()
        if not finito:  # Si le combat n'est pas fini, on termine le tour
            end_turn()
        

def take_quest():
    logger.info("📖")
    capture_full_window()
    quest = "quest"
    if Resolution == "1k":
        quest = "quest_1k"
    x, y = get_target_coords(quest, 0.8)
    if x != None:
        click_position(x, y, True)
        time.sleep(1)
        click_position(x + 35, y + 35)
        time.sleep(4.5)
    else:
        # On est toujours au soleil
        take_sun()
        take_quest()

def quit_malle():
    travel_command = f"/travel -25 -36"
    pyperclip.copy(travel_command) 
    write_in_chat()
    time.sleep(8.5)
    capture_full_window()
    if Resolution == "1k":
        quest = "quest_1k"
    x, y = get_target_coords(quest, 0.8)
    if x != None:
        quit_malle()


def trou_de_merde():
    pos = get_coo_actual()
    if pos != None:
        x,y = pos
        if x == -9 and y == -10:
            logger.info("Trou de merde")
            capture_full_window()
            x, y = get_target_coords("echelle", 0.7)
            if x != None:
                click_position(x  , y, True)
                time.sleep(3)


def map_koalak():
    pos = get_coo_actual()
    if pos != None:
        x,y = pos
        if x == -17 and y == 8:
            change_map("haut")
            time.sleep(5)

def map_buger_sans_havre_sac():
    pos = get_coo_actual()
    if pos != None:
        x,y = pos
        if x == 11 and y == 10:
            travel_command = f"/travel 10 10"
            pyperclip.copy(travel_command) 
            write_in_chat()
            time.sleep(8)


# def use_popo_rappel():
#     capture_full_window()
#     x, y = get_target_coords("popo_rappel", 0.8)
#     double_click_position(x,y)
#     time.sleep(6)




def go_havre_sac():
    logger.info("👜")

    trou_de_merde()
    map_koalak()
    #map_buger_sans_havre_sac()

    click_position_right(10, 500)
    time.sleep(0.5)
    keyboard.press_and_release('h')
    time.sleep(3.5)

    x, _ = find_zaap()

    if x is None:
        # logger.info("pas réussi a aller dans have sac")
        # logger.info("popo rappel ")
        # use_popo_rappel()

        # On bouge d'une map 
        change_map("gauche")
        go_havre_sac()
        

def sortir_havre_sac():
    logger.info("On sort 👜")

    time.sleep(0.5)
    keyboard.press_and_release('h')
    time.sleep(2)

def abandon_chasse():
    time.sleep(2)
    capture_full_window()
    x, y = get_target_coords("abandon", 0.8)
    if x != None:
        click_position(x  , y, True)

def chasse_en_cours():
    capture_full_window()
    x, y, width = get_target_coords_and_width("chasse", 0.8)
    if x != None:
        # On attend que le voyage est fini
        logger.info("Chasse en cours, on attend la fin du voyage (15 secondes)")
        time.sleep(15)
        click_position(width - 15 , y, True)
        return True
    return False

def find_zaap():
    capture_full_window()
    zaap = "zaap"
    if Resolution == "1k":
        zaap = "zaap_1k"
    x, y = get_target_coords(zaap, 0.8)

    return x,y
    

def open_zaap():
    x,y = find_zaap()
    click_position(x, y, True)
    time.sleep(2)


def sortir_pandala():
    sorti = False

    while not sorti:
        time.sleep(1)
        capture_full_window()
        pandala = "pandala"
        if Resolution == "1k":
            pandala = "pandala_1k"
        x, y = get_target_coords(pandala, 0.8)
        if x != None:
            click_position(x  , y, True)
            sorti = True
            logger.info("🐼 ✅")
        else : 
            logger.info("🐼 ❌")
    
    time.sleep(5)


def tp_near_zaap():
    try:

        capture_full_window()
        x, y = get_target_coords("depart", 0.8)
        region = (x + 30, y -20 , x + 120, y + 20 )
        capture_and_crop(region, "screen/depart_coo.png")
        x, y = extract_coo(extract_text("screen/depart_coo.png", coo=False), "screen/depart_coo.png")
        #logger.info(x, y)

        json = get_id_of_map(x, y)
        first_m_id = json["data"][0]["m_id"]
        #logger.info(first_m_id)

        json_2 = get_zaap_from_map(first_m_id)
        #logger.info(json_2)
        first_sub_area = json_2["data"][0]["hint"]["subareaId"]


        json_3 = get_name_area_from_id(first_sub_area)
        first_sub_area = json_3["name"]["fr"]
        #logger.info(first_sub_area)

        zaap_name = first_sub_area
        pyperclip.copy(zaap_name)
        #keyboard.press_and_release('ctrl+v')
        type_text_human_like(zaap_name, delay=0.15)
        time.sleep(1)        

        if "Désacrées" in zaap_name:
            time.sleep(60)
            raise Exception("Map buger on quitte cette chasse")
        
        keyboard.press_and_release('enter')

        time.sleep(5)

        if "Pandala" in zaap_name:
            # Faut sortir du bat car ça bug 
            sortir_pandala()
    

    except Exception as e:
        logger.info("On est bloqué dans le zaap")
        keyboard.press_and_release('esc')
        time.sleep(3)
        # On sort du havre sac
        sortir_havre_sac()
        time.sleep(3)
        raise Exception('On était bloqué dans le zaap')

    return x,y

def go_first_hint(x,y):

    if x == -26 and y == 28:
        # Cette pos bug 
        x = -26
        y = 29

    if x == 19 and y == -61:
        time.sleep(55)
        raise Exception("Map saharache bug")

    if x == -14 and y == 13:
        time.sleep(55)
        raise Exception("Map Morh kitu jeu de merde")

    if x == -81 and y == -37:
        time.sleep(55)
        raise Exception("Map frigost bug")

    extracted_coo_actual = get_coo_actual()
    if not compare_coordinates(extracted_coo_actual, [x, y]):
        travel_command = f"/travel {x} {y}"
        pyperclip.copy(travel_command) 
        write_in_chat()
        return x,y 
    else : 
        logger.info("On est déjà a la bonne map")
        return x,y 
    
def travel_finish(x, y):
    extracted_coo_actual = get_coo_actual()
    same_count = 0  # Compteur pour la répétition de la map (9, 21)

    time.sleep(4)

    while not compare_coordinates(extracted_coo_actual, [x, y]):
        extracted_coo_actual = get_coo_actual()
        logger.info(f"Voyage pos actuelle : {extracted_coo_actual}")

        if extracted_coo_actual == (0, 0):
            # Print c'est pas normal bloqué dans havre sac
            click_position_right(10, 500)
            time.sleep(0.5)
            sortir_havre_sac()
            raise Exception("Bloqué dans le havre sac à la pos 0,0")

        # Vérification spécifique pour la map (9, 21), en tenant compte des valeurs nulles
        if extracted_coo_actual == (9, 21) or extracted_coo_actual == None:
            same_count += 1
            if same_count >= 10:
                raise Exception(f"Blocage détecté : map {extracted_coo_actual} atteinte 10 fois de suite.")
        else:
            same_count = 0  # Réinitialise le compteur si la map change ou si c'est None

        time.sleep(2)

    return True

def get_text_from_chat():
    capture_bottom_left_corner()
    text = extract_text("screen/screen_chat.png")
    logger.info(text)
    return text


def find_malle_sur_la_map(image):
    capture_full_window()
    if image == 1 :
        x, y = get_target_coords("malle_map", 0.8)
    else : 
        x, y = get_target_coords("malle_map_2", 0.8)

    return x,y

def fix_la_map():
    
    move_mouse_smoothly(1900,1070,1)
    time.sleep(1)
    move_mouse_smoothly(500,500,1)

def go_cania():
    zaap_name = "champs de cania"
    pyperclip.copy(zaap_name)
    type_text_human_like(zaap_name, delay=0.15)
    time.sleep(1)
    keyboard.press_and_release('enter')
    time.sleep(4)
    fix_la_map()
    #go_first_hint(-25, -36)
    x,y = find_malle_sur_la_map(1)
    ctrl_click(x,y)
    time.sleep(10)
    x, _ = find_door()
    if x == None:
        logger.error('ctrl + clic a pas marché')
        x,y = find_malle_sur_la_map(2)
        ctrl_click(x,y)
        time.sleep(8)
    #chat = get_text_from_chat()
    # if "recherche"  in chat or "en cours" in chat :
    #     x,y = find_malle_sur_la_map(1)
    #     ctrl_click(x,y)
    #     time.sleep(15)
    #     x, _ = find_door()
    #     if x == None:
    #         logger.error('ctrl + clic a pas marché')
    #         x,y = find_malle_sur_la_map(2)
    #         ctrl_click(x,y)
    #         time.sleep(15)
    #         go_havre_sac()
    #         open_zaap()
    #         go_cania()
    # else : 
    #     time.sleep(10)

def type_text_human_like(text, delay=0.1):

    logger.info(text)
    """Simule la frappe lettre par lettre avec un délai."""
    for char in text:
        keyboard.write(char)  # Taper une lettre
        time.sleep(delay)  # Ajouter un délai entre chaque lettre

def press_enter():
    time.sleep(2)
    keyboard.press_and_release('enter')


def leave_chasse():
    logger.info('On regarde si chasse en cours')
    if chasse_en_cours():
        logger.info("On abandonne")
        abandon_chasse()
        press_enter()
        time.sleep(1)
        return False
    else:
        logger.info('Pas de chasse en cours')
        return True
    
def verif_max_chasse():
    time.sleep(1)
    chat = get_text_from_chat()
    if "chaque jour"  in chat or "Bien mal" in chat or "ne profite" in chat:
        logger.info(chat)
        logger.warning("Mise en veille du PC Imminente")
        time.sleep(1)
        logger.warning("3")
        time.sleep(1)
        logger.warning("2")
        time.sleep(1)
        logger.warning("1")
        time.sleep(1)
        os.system("rundll32.exe powrprof.dll,SetSuspendState Sleep")

    
if __name__ == "__main__":
    chasse_reussie = 0
    chasse_ratee = 0
    start_program_time = time.time()

    while True:
        try:
            os.system('cls' if os.name == 'nt' else 'clear')
            # Temps de début de l'itération actuelle
            start_time = time.time()

            # Afficher le récapitulatif avant chaque chasse
            total_runtime = time.time() - start_program_time
            logger.info("=" * 40)
            logger.info(f"Résumé des chasses :")
            logger.info(f"  - Chasses réussies : {chasse_reussie}")
            logger.info(f"  - Chasses ratées   : {chasse_ratee}")
            logger.info(f"  - Temps écoulé     : {total_runtime // 3600:.0f}h {total_runtime % 3600 // 60:.0f}m {total_runtime % 60:.0f}s")
            logger.info("=" * 40)

            leave_chasse()
            go_havre_sac()
            open_zaap()
            go_cania()
            take_door()
            take_sun()
            take_quest()
            verif_max_chasse()
            quit_malle()
            go_havre_sac()
            open_zaap()
            x,y = tp_near_zaap()
            
            x,y = go_first_hint(x,y)
            while travel_finish(x,y) == False:
                logger.info("")

            time.sleep(1)
            main()

            time.sleep(1)
            combat()
            time.sleep(3)
            logger.info("\n")
            press_enter()
            chasse_reussie += 1
            logger.info(f"Chasse réussie ! Temps pour cette chasse : { (time.time() - start_time) // 60 } minutes.\n")
            logger.info("\n")
            logger.info("\n")

        except Exception as e:
            logger.info(f"Une erreur inattendue s'est produite : {e}")
            logger.info("\n")
            logger.info("Redémarrage du processus principal...")
            chasse_ratee += 1
            logger.info("\n")
            while not leave_chasse():
                logger.info("")
            time.sleep(5)  # Pause avant de recommencer
