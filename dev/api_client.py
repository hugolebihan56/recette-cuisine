import json
import random
import sqlite3
import requests
from Levenshtein import distance as levenshtein_distance
import math
from logger_config import logger


def fetch_proxy_list(proxy_url):
    """
    Télécharge et retourne la liste des proxies depuis une URL donnée.
    
    Args:
        proxy_url (str): URL du fichier contenant les proxies sous la forme ip:port.
    
    Returns:
        list: Liste de proxies sous forme de dictionnaires {"ip": ..., "port": ...}.
    """
    try:
        response = requests.get(proxy_url, timeout=10)
        response.raise_for_status()  # Vérifie si l'URL est accessible sans erreur
        proxy_lines = response.text.splitlines()  # Divise le contenu par ligne
        proxies = []
        for line in proxy_lines:
            if ':' in line:
                ip, port = line.split(':')
                proxies.append({"ip": ip, "port": port})
        return proxies
    except requests.exceptions.RequestException as e:
        logger.info(f"Erreur lors de la récupération de la liste des proxies : {e}")
        return []

def call_bdd(current_x,current_y, direction):
    connection = sqlite3.connect('merged_database_v2.db')
    cursor = connection.cursor()

    distance = 15

    query_horizontal = """
    SELECT * 
    FROM points_of_interest 
    WHERE CAST(posX AS INTEGER) BETWEEN ? AND ? AND CAST(posY AS INTEGER) = ?
    """

    query_vertical = """
    SELECT * 
    FROM points_of_interest 
    WHERE CAST(posY AS INTEGER) BETWEEN ? AND ? AND CAST(posX AS INTEGER) = ?
    """

    # Paramètres de la requête
    if direction == '0':
        logger.info(f"Direction 0: x BETWEEN {current_x + 1} AND {current_x + distance}, y = {current_y}")
        cursor.execute(query_horizontal, (current_x + 1, current_x + distance, current_y))
    elif direction == '4':
        logger.info(f"Direction 4: x BETWEEN {current_x - distance} AND {current_x - 1}, y = {current_y}")
        cursor.execute(query_horizontal, (current_x - distance, current_x - 1,  current_y))
    elif direction == '6':
        logger.info(f"Direction 6: y BETWEEN {current_y - distance} AND {current_y - 1}  x = {current_x}")
        cursor.execute(query_vertical, (current_y - distance, current_y - 1,  current_x))
    elif direction == '2':
        logger.info(f"Direction 2: y BETWEEN {current_y + 1} AND {current_y + distance}, x = {current_x}")
        cursor.execute(query_vertical, (current_y + 1, current_y + distance, current_x))

    #logger.info("Appel bdd")
    # Récupération des résultats
    results = cursor.fetchall()

    # Nom des colonnes pour formater les résultats
    column_names = [description[0] for description in cursor.description]
    
    # Création d'un tableau de dictionnaires
    json_results = [dict(zip(column_names, row)) for row in results]

    # Fermeture de la connexion
    connection.close()

    # Retourner les résultats sous forme JSON
    return json.dumps(json_results, indent=4, ensure_ascii=False)
    
def send_treasure_hunt_request(x, y, direction, limit=50, lang='fr'):
    """
    Envoie une requête à l'API de chasse au trésor DofusDB.
    
    Args:
        x (int): Coordonnée X.
        y (int): Coordonnée Y.
        direction (int): Direction (1 = Haut, 2 = Droite, 3 = Bas, 4 = Gauche).
        limit (int): Limite des résultats. Par défaut : 50.
        lang (str): Langue des résultats. Par défaut : 'fr'.
    
    Returns:
        dict: Réponse JSON de l'API.
    """
    url = "https://api.dofusdb.fr/treasure-hunt"
    params = {
        "x": x,
        "y": y,
        "direction": direction,
        "$limit": limit,
        "lang": lang
    }

    proxy_url = "https://proxy.webshare.io/api/v2/proxy/list/download/imbdafrgxzxhlpbkjypmbcbvnhoatmffshqsemkq/-/any/sourceip/direct/-/"

    proxies_list = fetch_proxy_list(proxy_url) if proxy_url else []


    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Origin": "https://dofusdb.fr",
        "Referer": "https://dofusdb.fr/",
        "User-Agent":  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Token": "03AFcWeA5nHiayh_NCflC0ZiOKhGD33YywmzVIfp-zW6INURDD_IGnHqCeI9KN2HkFS6_qKypB64ZZNwjOe3tNAJaOJaDj465xnzsGX-HSOzdhVnNN3LZ_3dFBXP_HyWpoZ_LBSO6FXHCQFDV3NeNB1oItYB3KHnSCmNS1oF5eFCKXfPh_NvXNMvNDY8LLTAVECQtAIJB1KR9EdUhhYPoMy0EAjbKIvtv3dufjEUan-EuUq7piPq1E1uK-RVlQWaqGgVv7iXSp8c3sDdvc8PpU4nbO1Jc3Ac2EKtnSY53_9hM7Ek9NwzgUuEpFAcirSeV4tAsA3sGoyCOcjYPkIaTRXka8ZwoqFhJYbYPcapnFu0OxcGurVSL4CaA4XzMs9a7zAnnPMyIwyPF4_hzvOpjcFn_oz8ttYoY_jElKif1JkNTUUWDNXtpjigtg92M2c5xJ0xgixzubjRlEHlluDgQvmWfXvYiSJFNHCtmEA1tDzOasr-8OETjQYZ-m__bF71U2ebRs_JxqAJjl4mHkffxaxs46mfw2cCYyg0eoV07AOkJKTtpfvBSvnNO2DDcoOxN8JzCkK5EWIGv0ChGBSttQIhB1h77UcBUxNqZz6AZ-bwx9MC09t9TYnmzHY_Q9bGsEuSZkLEOYbefJUe4Fl87NJjykvHYTS1PoL5BhoSuiSKsj4C_Vuk0EvUDBhXo71RlVdBXPuaGym5N0keZpenaMsL298RRRfoit210YLZfjthirQJzKYpZescwP9uAC2EIZbnwg4Uh8I0GIoCDofwbGdvvQ1WHsMKzdr2fx9dFDYKiI4IsB4ZDXCoEMnCbGHbxVflYBf-XO0HZ5A7Lu0Lw7DYIZtuExydUgie4gBNOppPAxUsYvcpzAv8SZqRXqeBCyyEkjSZrnpD0eDKokWQn2b1T708yOB3Elew-VzbjaZ9vM0Ea_x_xN4jp_GufU3DY4wpuq66-x831dKw_oge3HaHJRRhqKTy6cfLSN5vX2TRrA8ih9cW9ItmbW7wKwtnob4Vfsvnq-3mLXLsSfM0KUdpL8bcHrhFMz5bGlDd1cvhb5NTkJ4-m93EPZBSzuh825ICti472K152lUInbG-Z9WLPU9P4BUEcLtkB4cRF-0a4t5PSQowmedit-RkCNryozqMWlklNYh6n-MgMJDNKkaockvqlxdoEMZTd5Xa9ZV9tHjxBz7mTIEb8DkuTxO4RYTOtMOh-Kkw3F-99vt_5_b93mTnLsLKq21H6WKxwQa9TEGv-G-8txtKXlx43dTisNDz2DyIik5i9gJF8hAEn0cq2Jcy-MLb9j3B4rhWK2EbME45VvQ3hD17HSLMUClpTcdJRuWXTgWd0GULEdXXvu3L879o7xfcneiWUJ1yKgIrk7IKURrPhnSnR-j2hyXDOA3iPHuJ7i32-DR3g_AbHRBkkm9kO00iIULoML5S8szBLjT5luadduEgK6QF7eHrtDI4_Z7OE3x-X869WbMXI0LqF3BoU3UmIe_HdLPxgLMAkNMva3dR8UerKM29ICzQt7YtJyu-ZsDnkDn9MOaHrvCzjb2MgcNr0aRYguGsq_1eXClRZ4-f6EcMO6tL-VoomVrE5QvJ4kt_PvskGOi0XhOG9allcumk_7-lnHMyQXgF3DYKqqwh1pguU74gg6N-6B9SZ5jL9wr_UKvstp-fX15GB0RZ-wVqll4JWog0D1yZNGvgdSxQ-qUAUHDnpmjWuoZ-rxFktUX6jzRSuPFD7OYuQTyd9Q0Nhhpp2vidzZYnFtsxO4C9yESILCCo6ZbRYoO8HfiwrLgbOJOA8pc1i3p_nsmJutnhXyLgyNk-4ARMX10rQ7TOvHsEPkF0_2eE8RW8EGSz0VeWlomYpIy8asnYSB15IhECJcaNN3_R27WfAk3SAkiDG7r2EgWWznFjtumLksTyw95R60AC75TVcCzD4T3Llt7mVof76yF9jYnTZ1IjNFR4KXKsmj58E8UevNJNjZpZQuU3kXtkX4gUsDMycYY-gVT_20Fm2nzM7walt9qXJp_e0fQDY"  # Remplace par ton token complet
    }



    chosen_proxy = random.choice(proxies_list)
    proxies = {
        "http": f"http://{chosen_proxy['ip']}:{chosen_proxy['port']}",
        "https": f"http://{chosen_proxy['ip']}:{chosen_proxy['port']}",
    }

    logger.info(f"Utilisation du proxy : {chosen_proxy['ip']}:{chosen_proxy['port']}")

    max_retries = 100

    for attempt in range(max_retries):
        # Choisir un proxy aléatoire
        chosen_proxy = random.choice(proxies_list)
        proxies = {
            "http": f"http://{chosen_proxy['ip']}:{chosen_proxy['port']}",
            "https": f"http://{chosen_proxy['ip']}:{chosen_proxy['port']}",
        }

        logger.info(f"Essai {attempt + 1}/{max_retries} avec le proxy : {chosen_proxy['ip']}:{chosen_proxy['port']}")

        try:
            response = requests.get(url, proxies=proxies, headers=headers, params=params, timeout=10)
            
            # Vérifie si la réponse est "NOT FOUND"
            if response.status_code == 404 or "NOT FOUND" in response.text:
                logger.info(f"Réponse NOT FOUND avec le proxy {chosen_proxy['ip']}. Test d'un autre proxy...")
                continue  # Réessayer avec un autre proxy

            if response.status_code != 200 or "OK" in response.text:
                logger.info(f"Réponse NOT OK avec le proxy {chosen_proxy['ip']}. Test d'un autre proxy...")
                continue  # Réessayer avec un autre proxy

            # Si tout va bien, retourne la réponse
            logger.info(f"Succès avec le proxy {chosen_proxy['ip']}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.info(f"Échec avec le proxy {chosen_proxy['ip']}. Erreur : {e}")
            continue  # Réessayer avec un autre proxy


def get_id_of_map(x,y):

    url = f"https://api.dofusdb.fr/map-positions?posX={x}&posY={y}"
    response = requests.get(url)
    return response.json()

def get_zaap_from_map(id):

    url = f"https://api.dofusdb.fr/transport-from-maps?id={id}"
    response = requests.get(url)
    return response.json()

def get_name_area_from_id(id):
    url = f"https://api.dofusdb.fr/subareas/{id}?lang=fr"
    response = requests.get(url)
    return response.json()



def get_pos_next_indice(api_response, indice, current_pos):
    """
    Recherche la position x et y la plus proche en fonction de l'indice, en combinant
    la distance de Levenshtein pour la similarité lexicale et la distance euclidienne
    pour la proximité spatiale.

    Args:
        api_response (dict): Réponse de l'API contenant les données.
        indice (str): L'indice à rechercher.
        current_pos (tuple): La position actuelle (x, y).

    Returns:
        tuple: Les coordonnées (x, y) si l'indice est trouvé, sinon None.
    """

    if "Phorreur" in indice:
        # Message stylisé
        logger.info("\n")
        logger.info("\n")

        logger.info("=" * 30)
        logger.info("🚨  PHORREUR DÉTECTÉ  🚨")
        logger.info("Détection en cours")
        logger.info("=" * 30 + "\n")
        logger.info("\n")
        logger.info("\n")


        return None, None

    def calculate_distance(pos1, pos2):
        """Calcule la distance euclidienne entre deux positions."""
        return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)

    def find_levenshtein_matches(api_response, indice):
        """
        Trouve toutes les correspondances basées sur la distance de Levenshtein.
        Retourne une liste de tuples (mot_API, position, distance_levenshtein).
        """
        matches = []
        for item in api_response:
            api_word = item["name_fr"]
            levenshtein_score = levenshtein_distance(indice, api_word)
            position = (item["posX"], item["posY"])
            matches.append((api_word, position, levenshtein_score))
        return matches


    # Rechercher les correspondances avec la distance de Levenshtein
    all_matches = find_levenshtein_matches(api_response, indice)

    # Filtrer pour garder uniquement les correspondances ayant la plus petite distance de Levenshtein
    if not all_matches:
        logger.info(f"Aucune correspondance trouvée pour '{indice}'.")
        return None

    min_levenshtein_distance = min(match[2] for match in all_matches)
    closest_levenshtein_matches = [
        match for match in all_matches if match[2] == min_levenshtein_distance
    ]

    # Si plusieurs correspondances ont la même distance de Levenshtein, utiliser la distance euclidienne
    if len(closest_levenshtein_matches) > 1:
        closest_match = min(
            closest_levenshtein_matches,
            key=lambda match: calculate_distance(current_pos, match[1])
        )
    else:
        closest_match = closest_levenshtein_matches[0]

    # Résultat final
    best_word, closest_position, _ = closest_match
    logger.info(f"Meilleure correspondance pour '{indice}': '{best_word}' à la position {closest_position}")
    return closest_position


def test_api():
    #proxi = urllib.request.getproxies()

    api_res = send_treasure_hunt_request(-1, -20, 6)
    new_pos = get_pos_next_indice(api_res, "Black Rose", (-1,20))
    logger.info(f"On va aller ici {new_pos}")

def test_proxy():
    url = "https://httpbin.org/ip"

    proxies = {
        "http": "http://C496HOPLY4NCG4KKA9AOH0KV3Z2WT58KOYMQUDLG52OI3RLRTMJS6Y93DR9BMJ1XQRM3WGY6MN6WX0WE:render_js=False&block_resources=False&premium_proxy=True@proxy.scrapingbee.com:8886",
        "https": "https://C496HOPLY4NCG4KKA9AOH0KV3Z2WT58KOYMQUDLG52OI3RLRTMJS6Y93DR9BMJ1XQRM3WGY6MN6WX0WE:render_js=False&block_resources=False&premium_proxy=True@proxy.scrapingbee.com:8887"
    }

    # Sans proxy
    response_no_proxy = requests.get(url)
    logger.info("Sans proxy:", response_no_proxy.json())

    # Avec proxy
    response_with_proxy = requests.get(url, proxies=proxies, verify=False)
    logger.info("Avec proxy:", response_with_proxy.json())

if __name__ == "__main__":
    #test_proxy()
    #test_api()
    json_result = call_bdd(7,-6,"4")
    logger.info(json_result)
    False