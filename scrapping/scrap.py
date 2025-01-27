import random
import threading
import requests
import sqlite3
import time

# Connexion à la base de données SQLite
conn = sqlite3.connect('dofus_map_reverse.db')
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

    def get_proxies():
        """
        Génère un dictionnaire de proxies à partir de la liste donnée.
        """
        chosen_proxy = random.choice(proxies_list)
        return {
            "http": f"http://ngrguayu:n6rhyptcinnw@{chosen_proxy['ip']}:{chosen_proxy['port']}",
            "https": f"http://ngrguayu:n6rhyptcinnw@{chosen_proxy['ip']}:{chosen_proxy['port']}",
        }

    def call_with_proxy(proxies):
        """
        Effectue la requête avec les proxies fournis.
        """
        response = requests.get(url, proxies=proxies)
        response.raise_for_status()  # Vérifie si la réponse HTTP est correcte (code 200)

        data = response.json()
        if data['total'] == 0:
            print(f"Pas de position valide pour ({x}, {y}). On passe à la prochaine.")
            return False  # Pas de positions valides trouvées
        return True  # Position valide

    try:
        # Appel initial avec un proxy choisi au hasard
        proxies = get_proxies()
        return call_with_proxy(proxies)

    except requests.exceptions.HTTPError as http_err:
        # Gérer les erreurs HTTP spécifiques
        if http_err.response.status_code == 404:
            print(f"Aucune donnée pour ({x}, {y}). On passe à la prochaine.")
            return False  # Aucune donnée trouvée
        else:
            print(f"Erreur HTTP {http_err.response.status_code} pour ({x}, {y}) : {http_err}")
            return False

    except requests.exceptions.RequestException as err:
        # Gérer les erreurs générales de requête (connexion, timeout, etc.)
        print(f"Erreur lors de la requête pour vérifier la position ({x}, {y}) : {err}")

        # Essayer avec un autre proxy
        proxies = get_proxies()
        try:
            return call_with_proxy(proxies)
        except requests.exceptions.RequestException as retry_err:
            print(f"Nouvel échec avec un autre proxy pour ({x}, {y}) : {retry_err}")
            return False

def fetch_and_save_points(x, y, direction, proxies_list, db_path):
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
        "Token": "03AFcWeA5MyM7l8PBfDKDrdVtXYQp9IRdzWJhTGwh-iurf14iOXiFWZD_3YANpFA_KCESib-OWKqzcqNaMY7YbeNsFepVHkXQ1U_Yhe7Z3TRnVs8yCf4CfdLeS5_wGNDiwSC2UDdD0x2GBZTJJ0mUjwVT9T0Sr7jFj_IB7TfJpinQgh79TwQM7XAvsZaJ496duZu338hRGf1zYTUGGIR_aKA_wtCIu_7eWemz7nAdBFLBEgLdKHSm8j-mVT5zaNljYo8XUXiTykiQK0UyarOy5FI-VJZxCvAcDiwsHRuxt9CnnCyflfl7op8TKa1KMu4vgJ6jlmJyRnaZiuO-87G1CCm4QWseIr0IJ3UoEWzns95LxB7AQL1JtLmMVudbsalQ-Njut5NlP7A9GSF1YS23Sdop46RfA9M3I9SG3XQuErcNkXT9-V-gP8oIfq0ZKOEHT-jAsjJDzNemC5Pieuq3f0-oHugqcExCitVXK1xv5UBUz6w4_svzZa7UJeTaPacEdm3Kti3WmN459wtC7Sm0tj03DeubrR663cycYBkmrrqWcQYb5wFwO_I6qreABpBEWV3YKPYiWrwSIHNNRNfx73UhOU5AY502Png8uuzArqOK15x9GLo-_Lg5fWg5cR68vTcvplYMgOHk-nUPLyAtCh9AmhyQnit_0MRTBLY9EVU7q7DPTkC16X0Px-JilEDqYt5n2lFqH3Ilh2c6q6_ZTGpnW1-hDWTYqgj_4vXbfArpGnHul5Kzi1K5WkyN3qrFejEcnWWdtxyAYgQmyaviTCOi3E_xqZk2UNhGOUdobmxYWF_0BE6_LZ4RninEWXBmUAMeH-eHGgdo268KJ4IPwbxptYkJdCYgGIQPZ25JPusLKSus2NJsCVmZJO3n4u4j8AKcJ-ChMdCaO9yG_DgnZqvmZtS3DH7qtFWUw5rf8D-5TxM-VNJDn-j85QKO0H52NutYVaF4iY7zJKgC1r36Dw4A5nzm81s2UGVlSBLtFARqu45Z8JxRHnTDil6rzUlmLYuVY9av9iPc3KJfISnodc9fnQpTnkWC7GLR_DRge07lGlV_wrOmC4Ds97tKKg9gv8ab5W57HOI9N6RaUSZUhqGx9VeIz8hlVP4uyK0kkelKORawJRui2EvndV2c167ZvR0xxhNPrvqA728XC7nPScQN2p30KKH8sOlqQV9Nrid8nPBrCWG15RIQ0RSMPzNBQdxGvQUy4C4CtbM0YrHFuOtqMLkAo6k6AgeqpYR0T4cxeGePSBtiHKzV863Se-rfE1fiD-mAzKFKKFK_xwJZHfAQtT6wWs3J5vbDyaVtPnAK28n4yYMgaSy-84lZ6GkHSiPQXe8vFmQDKqPfseJS1kdtpxlFVFghLoAlg6fV4zCG1uNYD4fh4__5GI7hASwUcSKmUHMJxK8iaBkaiwaaL8ugh4MapKEHbtnMcC2MFo4dcmWGZREM8KD-fGtYnWOu_i_TrFgh5iuswQAsHpHnsEGuXmGJv594V0kfwJ1ZUINrEUBgR1SXcSX0TqO-dnDr3_g4oLSkpnEA76mmVePWtWaKbsUd2L1JIZnHGP6W77IHZ3tvViiV_cDnvU7sx8kpZ7uaxqMIWPixHE1xK-lM6-jCDmzwzeciR0BEeH6t1J81FsJh_IQLUbSZ9bXgvNe503BgrHAvmeUYIdfLXllB7wlZo_TyX1hLRLRHBf0OE-BsC7BgGIirhLSdCiOMeL8Xbh49LIR5ZjfCz_MZDPLdQ9sfnWSyL9k0BevUlZLl5mPqRwqRL-FJLq94bnD1GvT63yvaUBAB9zyK-PspeYBHwDfj2nmeWTk_uJ3XPBsGpmxylYaPYSjJOcYXdb8XORmTLOm7PEqJ7yIVVLtWA5rz7tcx4Ezjq9Nx6UCksJbKnrM1K0DzgcwBLu1Axhnyp-hK_pC69raBHFb8x80dmvvpaBq3K-zCPMeTwuiDlDOjvrJYQSToa3YYj6GH3rl_oxl5EIWCvvIeVacmuWWHmz0By0h18uZSY0QF8Q5BkKswmWxQZFXSCzOS5tPWrcbEjffD5vAM0mx-oz2V_b_jtrn7p0FgAr9tVudkQNnnZ4_zPt_aL9pNbGjFCPVuQcOhAMbGjUG4Jn3cBVLoIQa5Bg2NR1bPf5nMc73rnMoNTZ7MG7-q3nCLuqbvFAnQBmuu08KjbPjfrZ_c4FtR_WBY6C70B8bm-lS4gQDpMdeat3tAbLj5OLJvxmkNXqStzPVDsPsBjb-Ft7xqvy19D"  # Remplace par ton token complet
    }

    chosen_proxy = random.choice(proxies_list)
    proxies = {
        "http": f"http://ngrguayu:n6rhyptcinnw@{chosen_proxy['ip']}:{chosen_proxy['port']}",
        "https": f"http://ngrguayu:n6rhyptcinnw@{chosen_proxy['ip']}:{chosen_proxy['port']}",
    }

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS points_of_interest (
            posX INTEGER,
            posY INTEGER,
            name_fr TEXT
        )
    """)
    conn.commit()

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
                conn.close()
                return max_x  # Retourne la coordonnée maximale x rencontrée

            else:
                conn.close()
                return x  # Retourne la coordonnée actuelle si aucune donnée trouvée


        elif response.status_code == 404:
            conn.close()
            print(f"Erreur 404 pour les coordonnées ({x}, {y}) avec direction {direction}. Aucun point d'intérêt trouvé.")
            return x  # Si 404, retourne x pour passer à la coordonnée suivante

        else:
            conn.close()
            print(f"Erreur HTTP {response.status_code} pour les coordonnées ({x}, {y}).")
            return x  # Retourne x si erreur HTTP

    except requests.exceptions.RequestException as err:
        conn.close()
        print(f"Erreur lors de la requête pour les coordonnées ({x}, {y}) : {err}")
        return x  # Retourne x si erreur lors de la requête

def get_all_points(min_x, max_x, path):
    """
    Récupère tous les points d'intérêt pour l'ensemble des positions sur la carte, de l'Est vers l'Ouest.
    """
    #min_x, max_x = -88, 28
    min_y, max_y = -71, 48

    # Récupérer la liste de proxies
    proxy_url = "https://proxy.webshare.io/api/v2/proxy/list/download/imbdafrgxzxhlpbkjypmbcbvnhoatmffshqsemkq/-/any/username/direct/-/"
    proxies_list = fetch_proxy_list(proxy_url)

    if not proxies_list:
        print("Aucun proxy disponible.")
        return

    # Direction Ouest (4)
    x = max_x
    while x >= min_x:  # Parcours de droite vers gauche
        y = min_y  # Commence à min_y pour chaque nouvelle coordonnée x

        while y <= max_y:  # Parcours les valeurs de y (de haut en bas)
            # Vérifie d'abord si la position est valide avant de continuer
            if check_map_position(x, y, proxies_list):
                new_x = fetch_and_save_points(x, y, 4, proxies_list, path)  # Direction Ouest
                if new_x == x:  # Si x n'a pas changé (aucun point d'intérêt trouvé ou erreur)
                    y += 1  # Passe à la coordonnée suivante sur l'axe y
                else:
                    x = new_x  # Sinon on passe à la coordonnée x maximale trouvée
            else:
                y += 1  # Si la position n'est pas valide, on passe à la suivante sur l'axe y

            # time.sleep(0.2)  # Pause de 1.5 seconde entre chaque requête

        x -= 1  # Une fois qu'on a terminé pour ce x, on passe au x précédent

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
        "Token": "03AFcWeA5MyM7l8PBfDKDrdVtXYQp9IRdzWJhTGwh-iurf14iOXiFWZD_3YANpFA_KCESib-OWKqzcqNaMY7YbeNsFepVHkXQ1U_Yhe7Z3TRnVs8yCf4CfdLeS5_wGNDiwSC2UDdD0x2GBZTJJ0mUjwVT9T0Sr7jFj_IB7TfJpinQgh79TwQM7XAvsZaJ496duZu338hRGf1zYTUGGIR_aKA_wtCIu_7eWemz7nAdBFLBEgLdKHSm8j-mVT5zaNljYo8XUXiTykiQK0UyarOy5FI-VJZxCvAcDiwsHRuxt9CnnCyflfl7op8TKa1KMu4vgJ6jlmJyRnaZiuO-87G1CCm4QWseIr0IJ3UoEWzns95LxB7AQL1JtLmMVudbsalQ-Njut5NlP7A9GSF1YS23Sdop46RfA9M3I9SG3XQuErcNkXT9-V-gP8oIfq0ZKOEHT-jAsjJDzNemC5Pieuq3f0-oHugqcExCitVXK1xv5UBUz6w4_svzZa7UJeTaPacEdm3Kti3WmN459wtC7Sm0tj03DeubrR663cycYBkmrrqWcQYb5wFwO_I6qreABpBEWV3YKPYiWrwSIHNNRNfx73UhOU5AY502Png8uuzArqOK15x9GLo-_Lg5fWg5cR68vTcvplYMgOHk-nUPLyAtCh9AmhyQnit_0MRTBLY9EVU7q7DPTkC16X0Px-JilEDqYt5n2lFqH3Ilh2c6q6_ZTGpnW1-hDWTYqgj_4vXbfArpGnHul5Kzi1K5WkyN3qrFejEcnWWdtxyAYgQmyaviTCOi3E_xqZk2UNhGOUdobmxYWF_0BE6_LZ4RninEWXBmUAMeH-eHGgdo268KJ4IPwbxptYkJdCYgGIQPZ25JPusLKSus2NJsCVmZJO3n4u4j8AKcJ-ChMdCaO9yG_DgnZqvmZtS3DH7qtFWUw5rf8D-5TxM-VNJDn-j85QKO0H52NutYVaF4iY7zJKgC1r36Dw4A5nzm81s2UGVlSBLtFARqu45Z8JxRHnTDil6rzUlmLYuVY9av9iPc3KJfISnodc9fnQpTnkWC7GLR_DRge07lGlV_wrOmC4Ds97tKKg9gv8ab5W57HOI9N6RaUSZUhqGx9VeIz8hlVP4uyK0kkelKORawJRui2EvndV2c167ZvR0xxhNPrvqA728XC7nPScQN2p30KKH8sOlqQV9Nrid8nPBrCWG15RIQ0RSMPzNBQdxGvQUy4C4CtbM0YrHFuOtqMLkAo6k6AgeqpYR0T4cxeGePSBtiHKzV863Se-rfE1fiD-mAzKFKKFK_xwJZHfAQtT6wWs3J5vbDyaVtPnAK28n4yYMgaSy-84lZ6GkHSiPQXe8vFmQDKqPfseJS1kdtpxlFVFghLoAlg6fV4zCG1uNYD4fh4__5GI7hASwUcSKmUHMJxK8iaBkaiwaaL8ugh4MapKEHbtnMcC2MFo4dcmWGZREM8KD-fGtYnWOu_i_TrFgh5iuswQAsHpHnsEGuXmGJv594V0kfwJ1ZUINrEUBgR1SXcSX0TqO-dnDr3_g4oLSkpnEA76mmVePWtWaKbsUd2L1JIZnHGP6W77IHZ3tvViiV_cDnvU7sx8kpZ7uaxqMIWPixHE1xK-lM6-jCDmzwzeciR0BEeH6t1J81FsJh_IQLUbSZ9bXgvNe503BgrHAvmeUYIdfLXllB7wlZo_TyX1hLRLRHBf0OE-BsC7BgGIirhLSdCiOMeL8Xbh49LIR5ZjfCz_MZDPLdQ9sfnWSyL9k0BevUlZLl5mPqRwqRL-FJLq94bnD1GvT63yvaUBAB9zyK-PspeYBHwDfj2nmeWTk_uJ3XPBsGpmxylYaPYSjJOcYXdb8XORmTLOm7PEqJ7yIVVLtWA5rz7tcx4Ezjq9Nx6UCksJbKnrM1K0DzgcwBLu1Axhnyp-hK_pC69raBHFb8x80dmvvpaBq3K-zCPMeTwuiDlDOjvrJYQSToa3YYj6GH3rl_oxl5EIWCvvIeVacmuWWHmz0By0h18uZSY0QF8Q5BkKswmWxQZFXSCzOS5tPWrcbEjffD5vAM0mx-oz2V_b_jtrn7p0FgAr9tVudkQNnnZ4_zPt_aL9pNbGjFCPVuQcOhAMbGjUG4Jn3cBVLoIQa5Bg2NR1bPf5nMc73rnMoNTZ7MG7-q3nCLuqbvFAnQBmuu08KjbPjfrZ_c4FtR_WBY6C70B8bm-lS4gQDpMdeat3tAbLj5OLJvxmkNXqStzPVDsPsBjb-Ft7xqvy19D"   # Remplace par ton token complet
    }
    #test_treasure_api_with_proxy_and_headers(proxies_list, headers)

    def thread_function(min_x, max_x, path):
        get_all_points(min_x, max_x, path)

    # Diviser la plage des X en zones
    global_min_x, global_max_x = -88, 28
    zones = [
        (-88, -60, "zone_1.db"),  # Zone 1mjje crois
        (-50, -34, "zone_2.db"),  # Zone 2
        (-25, -8, "zone_3.db"),    # Zone 3
        (0, 16, "zone_4.db"),    # Zone 4
    ]

    zones_sa = [
        (15, 15, "sa.db")
    ]

    # Chemins des bases de données associées aux zones
    db_paths = [
        "zone_1.db",  # Base de données pour Zone 1
        "zone_2.sdb",  # Base de données pour Zone 2
        "zone_3.db",  # Base de données pour Zone 3
        "zone_4.db",  # Base de données pour Zone 4
    ]

    # Créer et lancer les threads
    threads = []
    for min_x, max_x, path in zones:
        thread = threading.Thread(target=thread_function, args=(min_x, max_x, path))
        threads.append(thread)
        thread.start()

    # Attendre que tous les threads soient terminés
    for thread in threads:
        thread.join()

    #get_all_points()

    # Fermer la connexion à la base de données
    #conn.close()
