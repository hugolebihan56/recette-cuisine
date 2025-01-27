import ctypes
import math
import time
import pyautogui
import random
import keyboard  # Pour simuler les touches
from place_marker import load_coordinates
from pynput.keyboard import Controller, Key
from pyautogui import screenshot

# Définir les constantes pour simuler un clic de souris
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010

kb_controller = Controller()

# Fonction pour simuler un clic de souris
def mouse_event(flags, dx, dy, data, extra_info):
    ctypes.windll.user32.mouse_event(flags, dx, dy, data, extra_info)

def click():
    """Effectue un clic à la position actuelle de la souris."""
    x, y = pyautogui.position()  # Obtenir la position actuelle de la souris
    ctypes.windll.user32.SetCursorPos(x, y)  # Déplacer la souris à la position (x, y)
    time.sleep(0.1)  # Attendre un court instant pour stabiliser la position de la souris

    # Simuler un clic gauche (enfoncer le bouton)
    mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(random.uniform(0.05, 0.1))  # Attendre un délai aléatoire pour simuler un clic plus humain
    # Relâcher le bouton (fin du clic)
    mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

def auto_clicker(interval_min=0.1, interval_max=0.3, num_clicks=10):
    """
    Lance l'autoclicker qui effectue un nombre spécifié de clics
    avec un délai aléatoire entre chaque clic.
    """
    try:
        print(f"L'autoclicker est en marche, {num_clicks} clics à effectuer.")
        for _ in range(num_clicks):
            click()  # Effectuer le clic à la position actuelle de la souris
            interval = random.uniform(interval_min, interval_max)  # Intervalle aléatoire entre les clics
            time.sleep(interval)  # Attendre avant le prochain clic
    except KeyboardInterrupt:
        print("Autoclicker arrêté.")

def write_in_chat():
    """Effectue les actions demandées : clic gauche en bas à gauche, Ctrl+V et 2x Entrée"""
    # Déplacer la souris en bas à gauche de l'écran
    screen_width, screen_height = pyautogui.size()
    pyautogui.moveTo(random.uniform(90, 300), screen_height - random.uniform(9.0, 11.0))  # Bas à gauche de l'écran

    # Effectuer un clic gauche
    click()
    time.sleep(0.1)

    # Simuler un Ctrl + V pour coller
    keyboard.press_and_release('ctrl+v')
    time.sleep(0.4)  # Intervalle aléatoire après Ctrl+V

    # Simuler deux fois la touche Entrée

    keyboard.press_and_release('enter')
    time.sleep(0.5) 
    keyboard.press_and_release('enter') # Intervalle aléatoire entre les pressions de touche

def ctrl_click(x,y):
    """
    Effectue un Ctrl + clic gauche à la position actuelle de la souris.
    """
    move_mouse_smoothly(x,y)
    try:
        # Maintenir la touche Ctrl
        keyboard.press('ctrl')
        time.sleep(0.1)  # Petite pause pour s'assurer que Ctrl est bien enfoncé
        
        # Effectuer un clic gauche
        click()
    finally:
        # Relâcher la touche Ctrl
        keyboard.release('ctrl')

def hold_key_while_capturing(key, save_path):
    """
    Maintient une touche appuyée pendant la capture d'écran.

    :param key: La touche à maintenir (par exemple 'y').
    :param save_path: Chemin où la capture d'écran sera sauvegardée.
    """
    try:
        # Maintenir la touche appuyée
        kb_controller.press(key)
        time.sleep(0.5)

        # Effectuer la capture d'écran
        screenshot().save(save_path)
    finally:
        # Relâcher la touche après la capture
        kb_controller.release(key)


def click_position_right(x, y):

    # if x > 135 or x < 130:
    #     x = 132
    """Effectue un clic à la position spécifiée (x, y)."""
    ctypes.windll.user32.SetCursorPos(x, y)  # Déplacer la souris à la position (x, y)
    time.sleep(random.uniform(0.3, 0.4))  # Attendre un court instant pour stabiliser la position de la souris

    # Simuler un clic gauche (enfoncer le bouton)
    mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
    time.sleep(random.uniform(0.05, 0.1))  # Attendre un délai aléatoire pour simuler un clic plus humain
    # Relâcher le bouton (fin du clic)
    mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)

# Fonction pour obtenir la position actuelle de la souris
def get_mouse_position():
    cursor = ctypes.wintypes.POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(cursor))
    return cursor.x, cursor.y

def sigmoid(t):
    """Fonction sigmoïde pour lisser les transitions."""
    return 1 / (1 + math.exp(-10 * (t - 0.5)))


def go_left():
    keyboard.press_and_release("f3")

def go_up():
    keyboard.press_and_release("f1")

def go_right():
    keyboard.press_and_release("f4")

def go_down():
    keyboard.press_and_release("f2")

# Fonction pour déplacer la souris de manière fluide
def move_mouse_smoothly(x, y, duration=0.3):
    """
    Déplace la souris vers une position (x, y) avec une courbe de vitesse plus naturelle.
    """
    start_x, start_y = get_mouse_position()
    steps = max(int(duration * 100), 1)  # Nombre de pas pour le déplacement
    for i in range(steps + 1):
        # Calculer le facteur de progression avec la courbe sigmoïde
        t = sigmoid(i / steps)
        # Calculer les coordonnées intermédiaires
        current_x = int(start_x + t * (x - start_x))
        current_y = int(start_y + t * (y - start_y))
        ctypes.windll.user32.SetCursorPos(current_x, current_y)
        time.sleep(duration / steps)  # Pause entre chaque étape

def click_position(x, y, human=False):
    if human:
        move_mouse_smoothly(x, y, duration=random.uniform(0.5, 1.0))  # Déplacer avec un délai aléatoire
    else : 
        ctypes.windll.user32.SetCursorPos(x, y)  # Déplacer la souris à la position (x, y)
        
    time.sleep(random.uniform(0.3, 0.5))  # Pause après le déplacement
    # Simuler un clic gauche
    mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(random.uniform(0.05, 0.1))  # Délai aléatoire entre les actions
    mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)


def double_click_position(x, y, human=False):
    """
    Simule un double clic gauche à la position donnée (x, y).
    """
    # Déplace la souris à la position (x, y)
    if human:
        move_mouse_smoothly(x, y, duration=random.uniform(0.5, 1.0))  # Déplacer avec un délai aléatoire
    else:
        ctypes.windll.user32.SetCursorPos(x, y)  # Déplacer instantanément la souris à la position (x, y)
    
    time.sleep(random.uniform(0.3, 0.5))  # Pause après le déplacement
    
    # Simuler le premier clic gauche
    mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(random.uniform(0.05, 0.1))  # Délai aléatoire entre les actions
    mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    
    time.sleep(random.uniform(0.1, 0.2))  # Délai entre les deux clics (important pour le double clic)
    
    # Simuler le deuxième clic gauche
    mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(random.uniform(0.05, 0.1))  # Délai aléatoire entre les actions
    mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

def move(x, y): 
    """Effectue un clic à la position spécifiée (x, y)."""
    ctypes.windll.user32.SetCursorPos(x, y)  # Déplacer la souris à la position (x horizontalement , y verticalement) 
    time.sleep(0.1)  # Attendre un court instant pour stabiliser la position de la souris

# MARKER_X = 130
# MARKER_Y = 265

MARKER_X, MARKER_Y = load_coordinates()


def place_click_on_marker():
    move( ((MARKER_X) + 132), MARKER_Y + 12)


def valider(x,y):
    x = x + int(random.uniform(-1.0, 1.0))
    y = y + int(random.uniform(-1.0, 1.0))
    #move(x, y)
    click_position(MARKER_X + x, MARKER_Y + y)


if __name__ == "__main__":
    place_click_on_marker()
    #valider(132, 124)
    #move(262,286)
    
