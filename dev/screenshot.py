import pyautogui
from PIL import ImageGrab
import time

def capture_full_window(region=None):
    """
    Capture la fenêtre complète ou une région spécifiée.
    :param region: Tuple (x, y, width, height) pour capturer une région spécifique.
    :return: Image capturée.
    """
    screenshot = pyautogui.screenshot(region=region)
    filename = "screen/screen_global.png"
    screenshot.save(filename)
    return screenshot

def capture_full_window_datetime(region=None):
    """
    Capture la fenêtre complète ou une région spécifiée.
    :param region: Tuple (x, y, width, height) pour capturer une région spécifique.
    :return: Image capturée.
    """
    screenshot = pyautogui.screenshot(region=region)
    filename = f"Today/screenshot_archimonstre_{int(time.time())}.png"
    screenshot.save(filename)
    return filename

def capture_top_left_corner(width=200, height=200):
    """
    Capture une zone de la fenêtre de jeu dans le coin supérieur gauche.
    :param width: Largeur de la capture.
    :param height: Hauteur de la capture.
    :return: Image capturée.
    """
    screenshot = pyautogui.screenshot(region=(0, 0, width, height))
    filename = f"screenshot_top_left_{int(time.time())}.png"
    screenshot.save(filename)
    print(f"Capture du coin supérieur gauche enregistrée sous '{filename}'")
    return screenshot

def capture_bottom_right_corner(window_width=1920, window_height=1080, width=100, height=100):
    """
    Capture une zone de la fenêtre de jeu dans le coin inférieur droit.
    :param window_width: Largeur totale de la fenêtre.
    :param window_height: Hauteur totale de la fenêtre.
    :param width: Largeur de la capture.
    :param height: Hauteur de la capture.
    :return: Image capturée.
    """
    x = window_width - width
    y = window_height - height
    screenshot = pyautogui.screenshot(region=(x, y, width, height))
    filename = f"screenshot_bottom_right_{int(time.time())}.png"
    screenshot.save(filename)
    print(f"Capture du coin inférieur droit enregistrée sous '{filename}'")
    return screenshot

def capture_bottom_left_corner(window_width=1920, window_height=1080, width=350, height=45):
    """
    Capture une zone de la fenêtre de jeu dans le coin inférieur gauche.
    :param window_width: Largeur totale de la fenêtre.
    :param window_height: Hauteur totale de la fenêtre.
    :param width: Largeur de la capture.
    :param height: Hauteur de la capture.
    :return: Image capturée.
    """
    x = 10  # Position en x pour le coin inférieur gauche
    y = window_height - height  # Position en y reste identique
    screenshot = pyautogui.screenshot(region=(x, y, width, height))
    filename = "screen/screen_chat.png"
    screenshot.save(filename)
    #print(f"Capture du coin inférieur gauche enregistrée sous '{filename}'")
    return screenshot


def capture_custom_region(x, y, width, height):
    """
    Capture une zone personnalisée de la fenêtre de jeu.
    :param x: Position x de la zone de capture.
    :param y: Position y de la zone de capture.
    :param width: Largeur de la capture.
    :param height: Hauteur de la capture.
    :return: Image capturée.
    """
    screenshot = pyautogui.screenshot(region=(x, y, width, height))
    filename = f"screenshot_custom_{int(time.time())}.png"
    screenshot.save(filename)
    print(f"Capture de la région personnalisée enregistrée sous '{filename}'")
    return screenshot

def get_size_windows():

    screenshot = ImageGrab.grab()
    print(f"Taille de l'écran : hauteur={screenshot.height}, largeur={screenshot.width}")

    return screenshot.height, screenshot.width

def capture_and_crop(region, save_path):
    """
    Capture l'écran, recadre à une région spécifique et sauvegarde l'image.
    :param region: Tuple (left, top, right, bottom) pour la zone à recadrer.
    :param save_path: Chemin où sauvegarder l'image recadrée.
    :return: None
    """
    try:
        # Capture l'écran entier
        screenshot = ImageGrab.grab()

        # Recadrer l'image
        cropped_image = screenshot.crop(region)

        # Sauvegarder l'image
        cropped_image.save(save_path)
        #print(f"Image sauvegardée : {save_path}")
    except Exception as e:
        print(f"Erreur lors de la capture ou du recadrage : {e}")