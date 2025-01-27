import pytesseract
from PIL import  Image,  ImageEnhance
import re
import cv2
import matplotlib.pyplot as plt
import os
from config import Debug
import numpy as np
from autoclicker import MARKER_X, MARKER_Y
import sys

# Obtenir le répertoire du script Python courant
script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))

# Construire le chemin vers l'exécutable Tesseract
tesseract_path = os.path.join(script_dir, '../tesseract', 'tesseract.exe')

# Configurer pytesseract pour utiliser ce chemin
pytesseract.pytesseract.tesseract_cmd = tesseract_path

# Si Tesseract n'est pas dans le PATH système, spécifiez son chemin
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_coordinates(image_path):
    """
    Extrait les coordonnées entre crochets dans une image donnée.
    :param image_path: Chemin vers l'image à analyser.
    :return: Tuple contenant les coordonnées extraites (x, y) ou None si non trouvées.
    """
    try:
        # Charger l'image
        image = Image.open(image_path)

        # Utiliser Tesseract pour lire le texte
        text = pytesseract.image_to_string(image, lang="eng")
        print(f"Texte détecté : {text}")

        # Rechercher les coordonnées dans le texte ([x,y])
        match = re.search(r"\[(-?\d+),\s*(-?\d+)\]", text)
        if match:
            x, y = int(match.group(1)), int(match.group(2))
            print(f"Coordonnées détectées : ({x}, {y})")
            return x, y
        else:
            print("Aucune coordonnée trouvée dans l'image.")
            return None
    except Exception as e:
        print(f"Erreur lors de l'extraction des coordonnées : {e}")
        return None
    
def preprocess_image_path_advanced(image_path):
    """
    Applique un prétraitement sur l'image pour améliorer l'extraction de texte.
    :param image_path: Chemin vers l'image à traiter.
    :param debug: Active ou désactive les étapes de débogage.
    :return: Image PIL prétraitée.
    """

    # Charger l'image
    image = Image.open(image_path)

    # Convertir en niveaux de gris
    gray_image = image.convert('L')

    gray_image = gray_image.resize((gray_image.width * 2, gray_image.height * 2),Image.Resampling.LANCZOS)


    # Améliorer le contraste
    enhancer = ImageEnhance.Contrast(gray_image)
    enhanced_image = enhancer.enhance(1.5)

    # Convertir en format OpenCV
    open_cv_image = np.array(enhanced_image)

    # Appliquer un seuil binaire
    _, thresh_image = cv2.threshold(open_cv_image, 128, 255, cv2.THRESH_BINARY)

    # Reconvertir en image PIL
    final_image = Image.fromarray(thresh_image)

    # Visualiser les étapes
    if Debug:
        fig, axs = plt.subplots(4, 1, figsize=(8, 12))
        axs[0].imshow(image, cmap='gray')
        axs[0].set_title("Original Image")
        axs[1].imshow(gray_image, cmap='gray')
        axs[1].set_title("Grayscale Image")
        axs[2].imshow(enhanced_image, cmap='gray')
        axs[2].set_title("Enhanced Contrast Image")
        axs[3].imshow(final_image, cmap='gray')
        axs[3].set_title("Final Processed Image")
        plt.tight_layout()
        plt.show()

    return enhanced_image


def extract_text(image_path, coo=False):
    """
    Extrait le texte d'une région spécifique d'une image.
    :param image_path: Chemin vers l'image.
    :param region: Tuple (left, top, right, bottom) pour définir la région.
    :return: Texte extrait de la région.
    """
    try:
        # Charger l'image
        image = Image.open(image_path)
        
        preprocessed_image = preprocess_image_path(image_path)

        # Appliquer l'OCR pour extraire le texte

        #preprocessed_image_pil = Image.fromarray(preprocessed_image)

        #preprocessed_image_pil = preprocessed_image_pil.resize((preprocessed_image_pil.width * 2, preprocessed_image_pil.height * 2),Image.Resampling.LANCZOS)
        text = pytesseract.image_to_string(image, lang="eng")


        if text.strip() == '' or coo:
            if Debug:
                fig, axes = plt.subplots(1, 2, figsize=(12, 6))  # 1 ligne, 2 colonnes
                axes[0].imshow(image)
                axes[0].set_title("Image Originale")
                axes[0].axis('off')  # Supprimer les axes
                axes[1].imshow(preprocessed_image)
                axes[1].set_title("Image Prétraitée")
                axes[1].axis('off')  # Supprimer les axes
                plt.show()
            # Dans certaine zone le preprocess ne fonctionne pas bien
            image = image.resize((image.width * 2, image.height * 2),Image.Resampling.LANCZOS)
            text = pytesseract.image_to_string(image, lang="eng")

            if text.strip() == '' :
                preprocessed_image_ad = preprocess_image_path_advanced(image_path)
                text = pytesseract.image_to_string(preprocessed_image_ad, lang="eng")

        return text.strip()  # Nettoyer le texte
    except Exception as e:
        print(f"Erreur lors de l'extraction du texte : {e}")
        return None


def extract_coo(text, path):
    """
    Extrait les coordonnées x et y à partir d'une chaîne de texte.
    Le texte doit être au format : "Départ [x,y]".

    Args:
        text (str): Le texte contenant les coordonnées.

    Returns:
        tuple: Une paire (x, y) si les coordonnées sont trouvées, sinon None.
    """
    text = text.replace('.', ',')
    # Il ne peut pas y avoir de coordonées avec des + c'est surement un -
    text = text.replace('+', '-')
    # Le 1 confondu en I
    text = text.replace('I', '1')
    # Le 1 confondu en T
    text = text.replace('T', '1')
    # Le 1 confondu en l
    text = text.replace('l', '1')
    # Le 8 confondu en &
    text = text.replace('&', '8')
    # Le O confondu en 0
    text = text.replace('O', '0')
    text = text.replace('o', '0')
    text = text.replace('S', '5')
    text = text.replace('s', '5')
    text = text.replace(')', '1')

    text = re.sub(r'[^\d,\s\-]', '', text)  # Supprime les caractères non valides (garde chiffres, "-", "," et espaces)
    pattern = r"Start \[(-?\d+),(-?\d+)\]"
    match = re.search(pattern, text)
    if match:
        x = int(match.group(1))
        y = int(match.group(2))
        return x, y
    
    # Deuxième regex pour correspondre au format "x,y-[quelquechose]"
    pattern2 = r"(-?\d+)\s*,\s*(-?\d+)(?:\s*-.*)?\s*$"
    match = re.search(pattern2, text)
    
    if match:
        x = int(match.group(1))
        y = int(match.group(2))
        return x, y
    
    # Toujours aucune coordonées trouvé on va utiliser un nombre module d'OCR :
    #easy_ocr(path)

    return None  # Si l'une des parties n'est pas un nombre valide, retourner None



def count_indices(image_path):
    """
    Compte le nombre d'indices (ROIs) dans l'image en fonction des contours détectés,
    en excluant les rectangles isolés, sauf s'il n'y a qu'un seul rectangle.
    """
    # Charger l'image
    image = cv2.imread(image_path)

    # Convertir en niveaux de gris
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Appliquer un seuillage pour améliorer la détection de texte
    _, thresh = cv2.threshold(gray, 33, 255, cv2.THRESH_BINARY_INV)

    # Détecter les contours des zones de texte
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filtrer les contours pour exclure les zones trop grandes
    filtered_contours = []
    for contour in contours:
        epsilon = 0.01 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # Vérifie que le contour a 4 points et que les proportions sont correctes
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h
            if h <= 50 and h > 25 and aspect_ratio > 2:
                filtered_contours.append(contour)

    # Calculer les centres des rectangles
    bounding_boxes = [cv2.boundingRect(c) for c in filtered_contours]
    centers = [(x + w // 2, y + h // 2) for (x, y, w, h) in bounding_boxes]

    # Si un seul rectangle, il est accepté
    if len(centers) <= 1:
        return len(centers)

    # Filtrer les rectangles isolés
    isolated_threshold = 70  # Distance minimale entre les rectangles
    valid_contours = []
    for i, (cx, cy) in enumerate(centers):
        distances = [
            np.sqrt((cx - c[0]) ** 2 + (cy - c[1]) ** 2)
            for j, c in enumerate(centers) if i != j
        ]
        if any(d <= isolated_threshold for d in distances):
            valid_contours.append(filtered_contours[i])

    # Retourner le nombre de rectangles valides

    if len(valid_contours) == 0:
        valid_contours = filtered_contours

    return len(valid_contours)

def preprocess_arrow_image(image):
    """
    Applique un seuillage et un prétraitement pour améliorer la détection des flèches.
    """
    _, thresh = cv2.threshold(image, 150, 255, cv2.THRESH_BINARY)
    return thresh

def match_arrow(roi_left, arrow_dir):
    """
    Compare une région d'intérêt (roi_left) avec une flèche donnée (arrow_dir).
    Retourne un score de correspondance.
    """
    arrow_template = cv2.imread(arrow_dir, cv2.IMREAD_GRAYSCALE)
    arrow_template = preprocess_arrow_image(arrow_template)
    roi_left = preprocess_arrow_image(roi_left)

    # roi_left = cv2.resize(roi_left, (arrow_template.shape[1], arrow_template.shape[0]))  # Adapter la taille

    # if Debug:# Afficher les images pour le débogage avec plt
    #     plt.figure(figsize=(10, 5))

    #     # Afficher l'image du ROI
    #     plt.subplot(1, 2, 1)
    #     plt.imshow(roi_left, cmap='gray')
    #     plt.title("ROI Left")
    #     plt.axis('off')  # Supprimer les axes

    #     # Afficher l'image du modèle de flèche
    #     plt.subplot(1, 2, 2)
    #     plt.imshow(arrow_template, cmap='gray')
    #     plt.title("Arrow Template")
    #     plt.axis('off')  # Supprimer les axes

    #     plt.show()  # Afficher les images



    result = cv2.matchTemplate(roi_left, arrow_template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(result)
    return max_val

def detect_arrow_direction(roi_left):
    """
    Détecte la direction de la flèche dans la partie gauche du ROI.
    """
    arrow_dir_map = {
        '6': 'arrow/up.png',
        '2': 'arrow/down.png',
        '4': 'arrow/left.png',
        '0': 'arrow/right.png'
    }

    best_match = None
    best_score = 0

    # roi_left_preprocessed = preprocess_arrow_image(roi_left)

    for direction, template_path in arrow_dir_map.items():
        if os.path.exists(template_path):
            score = match_arrow(roi_left, template_path)
            if score > best_score:
                best_score = score
                best_match = direction

    return best_match



def extract_indice(image_path, index_indice):
    """
    Extrait un indice spécifique d'une image en fonction des contours détectés,
    tout en excluant les rectangles isolés, sauf s'il n'y a qu'un seul rectangle.
    """
    image_original = cv2.imread(image_path)
    image_modified = image_original.copy()

    # Convertir en niveaux de gris
    gray = cv2.cvtColor(image_modified, cv2.COLOR_BGR2GRAY)

    # Appliquer un seuillage pour améliorer la détection de texte
    _, thresh = cv2.threshold(gray, 33, 255, cv2.THRESH_BINARY_INV)

    # Détecter les contours des zones de texte
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filtrer les contours pour exclure les zones trop grandes
    filtered_contours = []
    for contour in contours:
        epsilon = 0.01 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # Vérifie que le contour a 4 points et que les proportions sont correctes
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h
            if h <= 50 and h > 25 and aspect_ratio > 2:
                filtered_contours.append(contour)

    # Calculer les centres des rectangles
    bounding_boxes = [cv2.boundingRect(c) for c in filtered_contours]
    centers = [(x + w // 2, y + h // 2) for (x, y, w, h) in bounding_boxes]


    # Filtrer les rectangles isolés
    isolated_threshold = 70 # Distance minimale entre les rectangles
    valid_contours = []
    for i, (cx, cy) in enumerate(centers):
        distances = [
            np.sqrt((cx - c[0]) ** 2 + (cy - c[1]) ** 2)
            for j, c in enumerate(centers) if i != j
        ]
        if any(d <= isolated_threshold for d in distances):
            valid_contours.append(filtered_contours[i])

    if len(valid_contours) == 0:
        valid_contours = filtered_contours


    # Trier les contours par position verticale
    final_contours = sorted(filtered_contours, key=lambda c: cv2.boundingRect(c)[1])

    # print(f"Nombre de contour touvé :  {len(filtered_contours)}")

    # Étape 5 : Afficher les contours après filtrage
    if Debug:
        # Créer une copie de l'image pour dessiner les contours filtrés
        debug_image_filtered = image_original.copy()
        cv2.drawContours(debug_image_filtered, final_contours, -1, (255, 0, 0), 2)  # Dessiner les contours filtrés en bleu
        plt.figure(figsize=(10, 6))
        plt.title("Contours détectés (après filtrage)")
        plt.imshow(cv2.cvtColor(debug_image_filtered, cv2.COLOR_BGR2RGB))
        plt.axis('off')
        plt.show()
    
    # Extraire et traiter chaque ligne de texte
    for i, contour in enumerate(final_contours):

        image_copy = image_original.copy()

        x, y, w, h = cv2.boundingRect(contour)

        image = preprocess_image(image_copy)

        # Diviser le ROI en deux parties (gauche et droite)
        roi = image[y:y+h, x:x+w]
        roi_left = roi[:, :23]  # Partie gauche (20 pixels)
        roi_center = roi[:, 20:w-70]

        # Vérifier si c'est l'indice souhaité
        if i + 1 == index_indice:
            arrow_direction = detect_arrow_direction(roi_left)

            text = pytesseract.image_to_string(roi_center, lang='eng+fra')  # Extraire le texte

            cleaned_text = re.sub(r'[^\w\s]', '', text)# Remplacer tout ce qui n'est pas une lettre ou un espace par rien

           # Ajouter les décalages pour obtenir les coordonnées globales du ROI

            x_coords = [point[0][0] for point in contour]  # Extraire les coordonnées x
            y_coords = [point[0][1] for point in contour]  # Extraire les coordonnées y

            center_x = int(sum(x_coords) / len(x_coords))  # Moyenne des x
            center_y = (int(sum(y_coords) / len(y_coords))) # - 28 #On veut cliquer sur l'indice précédent
            
            if Debug:
                plt.figure(figsize=(6, 4))
                plt.title(f"Texte a extraire {i+1}")
                plt.imshow(roi_center)
                plt.axis('off')
                plt.show()

            if center_x > 135 or center_x < 130:
                center_x = 132

            print(f"Contour {i + 1}: Centre = ({center_x}, {center_y})")

            #  # Étape 5 : Afficher chaque région d'intérêt (ROI)
            # plt.figure(figsize=(6, 4))
            # plt.title(f"Région d'intérêt {i+1}")
            # plt.imshow(cv2.cvtColor(roi_right, cv2.COLOR_BGR2RGB))
            # plt.axis('off')
            # plt.show()
            # if index_indice == 1:
            #     x_centre = 130 + 132
            #     y_centre = 240 + 35
            # else:

            x_centre = MARKER_X + center_x
            y_centre = MARKER_Y + center_y

            # print(x_centre, y_centre)

            # screenshot = ImageGrab.grab()

            # # Afficher un point (rouge) sur la capture d'écran globale
            # draw = ImageDraw.Draw(screenshot)
            # circle_radius = 10  # Rayon du cercle (augmenter si nécessaire)
            # draw.ellipse(
            #     [x_centre - circle_radius, y_centre - circle_radius, 
            #      x_centre + circle_radius, y_centre + circle_radius],
            #     fill='red'
            # )

            # # Sauvegarder l'image avec le cercle marqué
            # screenshot.save("debug_with_circle.png")

            #             # Afficher l'image avec matplotlib pour vérifier
            # plt.figure(figsize=(10, 6))
            # plt.title("Image avec cercle marqué")
            # plt.imshow(screenshot)
            # plt.axis('off')
            # plt.show()
            
            return arrow_direction, cleaned_text.strip(), [x_centre, y_centre]
        
def preprocess_image(image, scale=2.0, debug=False):
    """
    Prétraitement de l'image : agrandir, débruiter, appliquer un seuil, puis rescaler à la taille d'origine.
    
    :param image: Image d'entrée (numpy array).
    :param scale: Facteur d'agrandissement de l'image.
    :param debug: Afficher les étapes de traitement.
    :return: Image prétraitée (rescalée à la taille d'origine).
    """
    # Étape 1 : Agrandir l'image
    height, width = image.shape[:2]
    resized_image = cv2.resize(image, (int(width * scale), int(height * scale)), interpolation=cv2.INTER_CUBIC)

    # Étape 2 : Convertir en niveaux de gris
    grayscale_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)

    # Étape 3 : Débruiter l'image
    denoised_image = cv2.medianBlur(grayscale_image, 3)

    _, thresh_image = cv2.threshold(denoised_image, 128, 255, cv2.THRESH_BINARY_INV)

    inverted_image = cv2.bitwise_not(thresh_image)

    # Étape 5 : Rescaler à la taille d'origine
    rescaled_image = cv2.resize(inverted_image, (width, height), interpolation=cv2.INTER_AREA)

    if debug:
        # Visualiser les étapes
        steps = [("Original", image),
                 ("Resized", resized_image),
                 ("Grayscale", grayscale_image),
                 ("Denoised", denoised_image),
                 ("Threshold", thresh_image),
                 ("Rescaled to Original Size", rescaled_image)]
        plt.figure(figsize=(18, 10))
        for i, (title, step_image) in enumerate(steps):
            plt.subplot(1, len(steps), i + 1)
            plt.title(title)
            plt.imshow(step_image, cmap='gray')
            plt.axis('off')
        plt.show()

    return rescaled_image


def preprocess_image_path(image_path, debug=Debug):
    """
    Applique un prétraitement sur l'image pour améliorer l'extraction de texte.
    Affiche ou enregistre les étapes si debug est activé.
    :param image_path: Chemin vers l'image à traiter.
    :param debug: Active ou désactive les étapes de débogage.
    :return: Image prétraitée.
    """
    # Charger l'image
    image = Image.open(image_path)
    # Convertir en niveaux de gris
    gray_image = image.convert('L')
    # Améliorer le contraste pour rendre le texte plus visible
    enhancer = ImageEnhance.Contrast(gray_image)
    enhanced_image = enhancer.enhance(2)  # Augmenter le contraste
    # Convertir l'image en format numpy pour utiliser avec OpenCV si nécessaire
    open_cv_image = np.array(enhanced_image)
    # Appliquer un seuil pour améliorer la détection des contours du texte
    _, thresh_image = cv2.threshold(open_cv_image, 128, 255, cv2.THRESH_BINARY_INV)
    # Convertir l'image prétraitée en image PIL
    final_image = Image.fromarray(open_cv_image)

    if debug:
        fig, axs = plt.subplots(3, 2, figsize=(10, 10))
        axs = axs.ravel()  # Aplatir le tableau pour faciliter l'indexation

        # Afficher l'image originale
        axs[0].imshow(image, cmap='gray')
        axs[0].set_title("Original Image")
        axs[0].axis('off')

        axs[1].imshow(gray_image, cmap='gray')
        axs[1].set_title("Grayscale Image")
        axs[1].axis('off')

        axs[2].imshow(enhanced_image, cmap='gray')
        axs[2].set_title("Enhanced Contrast Image")
        axs[2].axis('off')

        axs[3].imshow(thresh_image, cmap='gray')
        axs[3].set_title("Thresholded Image")
        axs[3].axis('off')

        axs[4].imshow(final_image, cmap='gray')
        axs[4].set_title("Final Processed Image")
        axs[4].axis('off')

        plt.tight_layout()
        plt.show()
    return thresh_image

def test_indice_extracor():
    indice = 1
    output_dir = "screen"
    save_path = os.path.join(output_dir, "screen_zone.png")
    arrow_dir_map = {
        '6': 'arrow/up.png',
        '2': 'arrow/down.png',
        '4': 'arrow/left.png',
        '0': 'arrow/right.png'
    }
    arrow_direction, extracted_text, marker_coo = extract_indice(save_path, indice)
    print(extracted_text)
    print(arrow_direction)

def test_coo_extractor():
    output_dir = "screen"
    save_path_coo_actual = os.path.join(output_dir, "coo_actual.png")
    extracted_coo_actual = extract_coo(extract_text(save_path_coo_actual, coo=True), save_path_coo_actual)
    print(extracted_coo_actual)


if __name__ == "__main__":
    test_coo_extractor() 
    #test_indice_extracor()
    False