import random
import requests
import sqlite3
import time

# Connexion à la base de données SQLite
conn = sqlite3.connect('dofus_map_v3_2.db')
cursor = conn.cursor()

# Création de la table pour stocker les points d'intérêt
cursor.execute('''CREATE TABLE IF NOT EXISTS points_of_interest (
                    id INTEGER PRIMARY KEY,
                    posX INTEGER,
                    posY INTEGER,
                    name_fr TEXT
                )''')
conn.commit()

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
                ip, port, i, p = line.split(':')
                proxies.append({"ip": ip, "port": port})
        return proxies
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la récupération de la liste des proxies : {e}")
        return []

def check_map_position(x, y, proxies_list):
    """
    Vérifie si la position donnée existe sur la carte.
    """
    url = f'https://api.dofusdb.fr/map-positions?posX={x}&posY={y}'

    chosen_proxy = random.choice(proxies_list)
    proxies = {
        "http": f"http://ngrguayu:n6rhyptcinnw@{chosen_proxy['ip']}:{chosen_proxy['port']}",
        "https": f"http://ngrguayu:n6rhyptcinnw@{chosen_proxy['ip']}:{chosen_proxy['port']}",
    }

    def call():
        response = requests.get(url, proxies=proxies)
        response.raise_for_status()  # Vérifie si la réponse HTTP est correcte (code 200)
        
        if response.status_code == 200:
            data = response.json()
            if data['total'] == 0:
                print(f"Pas de position valide pour ({x}, {y}). On passe à la prochaine.")
                return False
            return True
        else:
            print(f"Erreur HTTP {response.status_code} pour les coordonnées ({x}, {y})")
            return False

    try:
        return call()
        
    except requests.exceptions.RequestException as err:

        print(f"Erreur lors de la requête pour vérifier la position ({x}, {y}) : {err}")
        chosen_proxy = random.choice(proxies_list)
        return call()


def fetch_and_save_points(x, y, direction, proxies_list):
    """
    Récupère les points d'intérêt pour la position donnée et les enregistre dans la base de données.
    """
    url = f'https://api.dofusdb.fr/treasure-hunt?x={x}&y={y}&direction={direction}&$limit=50&lang=fr'

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Origin": "https://dofusdb.fr",
        "Referer": "https://dofusdb.fr/",
        "User-Agent":  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Token": "03AFcWeA7Rd8Wz1CYwTo0t-U_TT4_xNEhz9TGEeGQqwjmzDqU410wWP5zJUjraeDhE-VU-puKz2XTdSf3453vEOMoSjQE8Dkgf5O8-XC8VVX49NgaNvoL9phK5Ranjmnod5gWEcjNl9LkjwnN-i5yyYXvSGPvd6dTX2yiV3C2DipsqQ6-nxypojqMteCEJu0ClzcirXzBZ6fRK_JtzyhvLC6rch1gr1rYh8Gnhy0sBsLVkFOhKumuigGvCx9HN4Wo8vFYR-SNk6zAYcBqFikRP7_NiiD11dxrFR0Y8oa56_m9DD8zjHaCdN35QfkFKESt6Xbg9CAbUlZ8VGfWLrfV9FDwANnPpKd4YZWi-qzjLXBjGH4rdWq49WQ8rMXd5p8CwMFoDu89MxboIUT6pOJaZZYvKBK-u6md4BKbqvgMQVfS1MMvX6iHn7Lsb-QxAtWWXPzf1XOmIMEkM57hzwyI2umsjM41po9qxVtWuAhdnqBYTzQHezy9p1RzY4MapiolmMRpQFRLqM2vHiSX_xp6WjzBSdSCOSQ9CZVtNBAvQ_IvLmv3BG5AElKKmX_6_WDdkw14-czTjJox0vt1_S6TmsMfKVvP0FTmH_-whVbxywQCdpnc6xZ4dzfig6Ps3sH1dYMwoBelYVlB-FTCsxyUwOXcT7secsfl3S_aNBs28RDrjmDoS3cZGAMKX_PB1AbJnouRrdE0o5wozlq9ZT5iLd-_2a3kDRV1yvMh3jD4n5VUrOosFJW9lO0NVdjihP3SKak_Maj99sY0FlLcScLXtWdyIraOJfkgTQuETYbT0RPLD-8O0qYjx1kxHa6k47Orl4sBG2kDVkPSB7KBLGWjWwmPBLsbq2dMMUs4395TFCkGiIhKLAD20TyemlEneIocaZ069tWveKHbXT4o9yIpSSuZSVBFGJG4p9Qld_qksxKqePrPqStPBqKZP_irt6bUj4zb7PEM2JapGj8ZT-qEPC1sDO75oXTswxKByISfSJj6ZHZkQ3TSRvzSqkN2zDC5pCSkyAKwCxELxePoAELw7txm4URuJxZuDxRu5H_Gd1DvuZedVdCE6EfhHheWROawp--z0qUEnxruvk2_7Yd3Wu9PPSlOpxgLEQ0evE5pIheNRCPZh-vydmHIb3hRwxkVil96zMBk1ST85aBUc5FRfEbhLB6hZLGMHDTgf7Bwcof0EVKztxVw4CXEgkbPjZyMmVgAnUUpbuHGj1mvglU_e1d724pafTHmn9Wewa9Qa-F2Kb7DzObZ9sa3tl-2hgSQB_qNVusvLmIijWQyQmSzEk2A3EFmIj93IYCEYJTXZkVhvQfUxzShrLy0NnpSRP5V84GOgFyCIlvPyFAMGRS_ns3ECotcKlczLAXtkKg4S5Qj2XofAEKsAM5gH_p2iNCZ9CH2ISPaKUdMq-t5-NTnead1nb48rg6lzVNJ3emj2B56dht0tlKHEAmhJUdz0Cq3G0kqlN88zbWRnr_5VQUfZ4Bw00qT_ZNJp27tGmvfFmW_xxFNhlCay7DscBiI4mlBbGImQPC1srBaC7T34Xd9IuEevjTJQCIqYPNRcMF2jBahZkzb9tScUMrZPkcrf_CcikyKHIBNzn6TaHbYSqZGDwhaUUwRHaPDKA20ZCZCF1xKI_KbAov62H7DPh32VMz5DPnsCYbjVB8gbwFpJu1miklOiVJ7KUbqbDKHW-eAj2j7frosVsS-aPW4o5nxGM9GOKphwmjuQdCTUDoZEA-FYcJdOfS-r-5MPrCmFQu7wZbfRuFk0Bp1pBQSNAb3K1qqKInmzIvbt9ED9zGjMOtVnFqIxNF7PZFubagmgxw2PUoQnf1xJQQMvxr1T8Jprcpjq4iWBaZW2NB3Ky3vXIy4aM4_R0Cx64JGYZjzJwDO3cG4lD8F0EJiHB_seOd3-TK9SLEkg97A-kR8a2rEUJjF-Hw4GUORomkV7-A"  # Remplace par ton token complet
    }

    max_retries = 50
    chosen_proxy = random.choice(proxies_list)
    proxies = {
        "http": f"http://ngrguayu:n6rhyptcinnw@{chosen_proxy['ip']}:{chosen_proxy['port']}",
        "https": f"http://ngrguayu:n6rhyptcinnw@{chosen_proxy['ip']}:{chosen_proxy['port']}",
    }

    try:
        response = requests.get(url, proxies=proxies, headers=headers)
        response.raise_for_status()  # Vérifie si la réponse HTTP est correcte (code 200)

        if response.status_code == 200:
            data = response.json()
            print(f"Position valide ({x}, {y}). On insère.")
            if data["total"] > 0:
                max_x = x
                for poi_group in data["data"]:  # Chaque groupe de POI
                    posX = poi_group["posX"]
                    posY = poi_group["posY"]
                    # Récupérer tous les POI pour cette position
                    pois_to_insert = []
                    for poi in poi_group["pois"]:
                        name_fr = poi["name"]["fr"]
                        pois_to_insert.append((posX, posY, name_fr))  # Ajoute les POI à une liste

                    # Insertion dans la base de données après avoir collecté tous les POI
                    cursor.executemany("INSERT INTO points_of_interest (posX, posY, name_fr) VALUES (?, ?, ?)",
                                    pois_to_insert)
                    conn.commit()

                return max_x  # Retourne la coordonnée maximale x rencontrée

            else:
                return x  # Retourne la coordonnée actuelle si aucune donnée trouvée


        elif response.status_code == 404:
            print(f"Erreur 404 pour les coordonnées ({x}, {y}) avec direction {direction}. Aucun point d'intérêt trouvé.")
            return x  # Si 404, retourne x pour passer à la coordonnée suivante

        else:
            print(f"Erreur HTTP {response.status_code} pour les coordonnées ({x}, {y}).")
            return x  # Retourne x si erreur HTTP

    except requests.exceptions.RequestException as err:
        print(f"Erreur lors de la requête pour les coordonnées ({x}, {y}) : {err}")
        return x  # Retourne x si erreur lors de la requête

def get_all_points():
    """
    Récupère tous les points d'intérêt pour l'ensemble des positions sur la carte, de l'Ouest vers l'Est.
    """
    min_x, max_x = -20, 0
    min_y, max_y = -71, 48

    # Récupérer la liste de proxies
    proxy_url = "https://proxy.webshare.io/api/v2/proxy/list/download/imbdafrgxzxhlpbkjypmbcbvnhoatmffshqsemkq/-/any/username/direct/-/"
    proxies_list = fetch_proxy_list(proxy_url)

    if not proxies_list:
        print("Aucun proxy disponible.")
        return

    # Direction Est (0)
    x = min_x
    while x <= max_x:
        y = min_y  # Commence à min_y pour chaque nouvelle coordonnée x
        
        while y <= max_y:  # Parcours les valeurs de y (de haut en bas)
            # Vérifie d'abord si la position est valide avant de continuer
            if check_map_position(x, y, proxies_list):
                new_x = fetch_and_save_points(x, y, 0, proxies_list)  # Direction Est
                if new_x == x:  # Si x n'a pas changé (aucun point d'intérêt trouvé ou erreur)
                    y += 1  # Passe à la coordonnée suivante sur l'axe y
                else:
                    x = new_x  # Sinon on passe à la coordonnée x maximale trouvée
            else:
                y += 1  # Si la position n'est pas valide, on passe à la suivante sur l'axe y

            #time.sleep(0.2)  # Pause de 1.5 seconde entre chaque requête

        x += 1  # Une fois qu'on a terminé pour ce x, on passe au x suivant

    print("Données collectées et sauvegardées dans la base de données.")

# Lancer la collecte de points d'intérêt


def test_treasure_api_with_proxy_and_headers(proxy_list, headers, x=0, y=0, direction=0):
    """
    Teste l'API Trésor avec des coordonnées données (x, y), un proxy et des headers.

    Args:
        proxy_list (list): Liste de proxies sous forme de dictionnaires {"ip": ..., "port": ...}.
        headers (dict): Dictionnaire contenant les headers à envoyer avec la requête.
        x (int): Coordonnée x pour la requête (par défaut 0).
        y (int): Coordonnée y pour la requête (par défaut 0).
        direction (int): Direction de la recherche (par défaut 0, pour Est).

    Returns:
        None: Affiche la réponse de l'API ou un message d'erreur.
    """
    url = f'https://api.dofusdb.fr/treasure-hunt?x={x}&y={y}&direction={direction}&$limit=50&lang=fr'



    # Choisir un proxy aléatoire
    chosen_proxy = random.choice(proxies_list)
    proxies = {
        "http": f"http://{chosen_proxy['ip']}:{chosen_proxy['port']}",
        "https": f"http://{chosen_proxy['ip']}:{chosen_proxy['port']}",
    }

    try:
        # Effectuer la requête avec le proxy et les headers
        response = requests.get(url, proxies=proxies, headers=headers)
        response.raise_for_status()  # Vérifie si la réponse HTTP est correcte (code 200)

        if response.status_code == 200:
            data = response.json()
            print("Données reçues de l'API :")
            print(data)  # Affiche les données renvoyées par l'API
        else:
            print(f"Erreur HTTP {response.status_code} pour les coordonnées ({x}, {y}).")

    except requests.exceptions.RequestException as err:
        print(f"Erreur lors de la requête pour les coordonnées ({x}, {y}) : {err}")


if __name__ == "__main__":

    proxy_url = "https://proxy.webshare.io/api/v2/proxy/list/download/imbdafrgxzxhlpbkjypmbcbvnhoatmffshqsemkq/-/any/username/direct/-/"
    proxies_list = fetch_proxy_list(proxy_url)

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Origin": "https://dofusdb.fr",
        "Referer": "https://dofusdb.fr/",
        "User-Agent":  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Token": "03AFcWeA7Rd8Wz1CYwTo0t-U_TT4_xNEhz9TGEeGQqwjmzDqU410wWP5zJUjraeDhE-VU-puKz2XTdSf3453vEOMoSjQE8Dkgf5O8-XC8VVX49NgaNvoL9phK5Ranjmnod5gWEcjNl9LkjwnN-i5yyYXvSGPvd6dTX2yiV3C2DipsqQ6-nxypojqMteCEJu0ClzcirXzBZ6fRK_JtzyhvLC6rch1gr1rYh8Gnhy0sBsLVkFOhKumuigGvCx9HN4Wo8vFYR-SNk6zAYcBqFikRP7_NiiD11dxrFR0Y8oa56_m9DD8zjHaCdN35QfkFKESt6Xbg9CAbUlZ8VGfWLrfV9FDwANnPpKd4YZWi-qzjLXBjGH4rdWq49WQ8rMXd5p8CwMFoDu89MxboIUT6pOJaZZYvKBK-u6md4BKbqvgMQVfS1MMvX6iHn7Lsb-QxAtWWXPzf1XOmIMEkM57hzwyI2umsjM41po9qxVtWuAhdnqBYTzQHezy9p1RzY4MapiolmMRpQFRLqM2vHiSX_xp6WjzBSdSCOSQ9CZVtNBAvQ_IvLmv3BG5AElKKmX_6_WDdkw14-czTjJox0vt1_S6TmsMfKVvP0FTmH_-whVbxywQCdpnc6xZ4dzfig6Ps3sH1dYMwoBelYVlB-FTCsxyUwOXcT7secsfl3S_aNBs28RDrjmDoS3cZGAMKX_PB1AbJnouRrdE0o5wozlq9ZT5iLd-_2a3kDRV1yvMh3jD4n5VUrOosFJW9lO0NVdjihP3SKak_Maj99sY0FlLcScLXtWdyIraOJfkgTQuETYbT0RPLD-8O0qYjx1kxHa6k47Orl4sBG2kDVkPSB7KBLGWjWwmPBLsbq2dMMUs4395TFCkGiIhKLAD20TyemlEneIocaZ069tWveKHbXT4o9yIpSSuZSVBFGJG4p9Qld_qksxKqePrPqStPBqKZP_irt6bUj4zb7PEM2JapGj8ZT-qEPC1sDO75oXTswxKByISfSJj6ZHZkQ3TSRvzSqkN2zDC5pCSkyAKwCxELxePoAELw7txm4URuJxZuDxRu5H_Gd1DvuZedVdCE6EfhHheWROawp--z0qUEnxruvk2_7Yd3Wu9PPSlOpxgLEQ0evE5pIheNRCPZh-vydmHIb3hRwxkVil96zMBk1ST85aBUc5FRfEbhLB6hZLGMHDTgf7Bwcof0EVKztxVw4CXEgkbPjZyMmVgAnUUpbuHGj1mvglU_e1d724pafTHmn9Wewa9Qa-F2Kb7DzObZ9sa3tl-2hgSQB_qNVusvLmIijWQyQmSzEk2A3EFmIj93IYCEYJTXZkVhvQfUxzShrLy0NnpSRP5V84GOgFyCIlvPyFAMGRS_ns3ECotcKlczLAXtkKg4S5Qj2XofAEKsAM5gH_p2iNCZ9CH2ISPaKUdMq-t5-NTnead1nb48rg6lzVNJ3emj2B56dht0tlKHEAmhJUdz0Cq3G0kqlN88zbWRnr_5VQUfZ4Bw00qT_ZNJp27tGmvfFmW_xxFNhlCay7DscBiI4mlBbGImQPC1srBaC7T34Xd9IuEevjTJQCIqYPNRcMF2jBahZkzb9tScUMrZPkcrf_CcikyKHIBNzn6TaHbYSqZGDwhaUUwRHaPDKA20ZCZCF1xKI_KbAov62H7DPh32VMz5DPnsCYbjVB8gbwFpJu1miklOiVJ7KUbqbDKHW-eAj2j7frosVsS-aPW4o5nxGM9GOKphwmjuQdCTUDoZEA-FYcJdOfS-r-5MPrCmFQu7wZbfRuFk0Bp1pBQSNAb3K1qqKInmzIvbt9ED9zGjMOtVnFqIxNF7PZFubagmgxw2PUoQnf1xJQQMvxr1T8Jprcpjq4iWBaZW2NB3Ky3vXIy4aM4_R0Cx64JGYZjzJwDO3cG4lD8F0EJiHB_seOd3-TK9SLEkg97A-kR8a2rEUJjF-Hw4GUORomkV7-A"  # Remplace par ton token complet
    }
    #test_treasure_api_with_proxy_and_headers(proxies_list, headers)

    get_all_points()

    # Fermer la connexion à la base de données
    conn.close()
