import sqlite3
import requests
import random

from github import maj_bdd

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

def get_treasure_hunt():
    # Demander les coordonnées et la direction à l'utilisateur
    insert = False
    print("\n")
    print("Coordonnées de la map du début de la recherche (pas de là où doit etre l'indice)")
    print("\n")
    x = input("Entrez la coordonnée X : ")
    y = input("Entrez la coordonnée Y : ")
    direction = input("Entrez la direction (ex: nord, sud, est, ouest) : ")

    if direction == "nord":
        direction = 6
    elif direction == "sud":
        direction = 2
    elif direction == "est":
        direction = 0
    elif direction == "ouest":
        direction = 4

    # Construire l'URL de l'API avec les paramètres
    url = f'https://api.dofusdb.fr/treasure-hunt?x={x}&y={y}&direction={direction}&$limit=50&lang=fr'

    # Définir les en-têtes de la requête
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Origin": "https://dofusdb.fr",
        "Referer": "https://dofusdb.fr/",
        "User-Agent":  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Token": "03AFcWeA5MyM7l8PBfDKDrdVtXYQp9IRdzWJhTGwh-iurf14iOXiFWZD_3YANpFA_KCESib-OWKqzcqNaMY7YbeNsFepVHkXQ1U_Yhe7Z3TRnVs8yCf4CfdLeS5_wGNDiwSC2UDdD0x2GBZTJJ0mUjwVT9T0Sr7jFj_IB7TfJpinQgh79TwQM7XAvsZaJ496duZu338hRGf1zYTUGGIR_aKA_wtCIu_7eWemz7nAdBFLBEgLdKHSm8j-mVT5zaNljYo8XUXiTykiQK0UyarOy5FI-VJZxCvAcDiwsHRuxt9CnnCyflfl7op8TKa1KMu4vgJ6jlmJyRnaZiuO-87G1CCm4QWseIr0IJ3UoEWzns95LxB7AQL1JtLmMVudbsalQ-Njut5NlP7A9GSF1YS23Sdop46RfA9M3I9SG3XQuErcNkXT9-V-gP8oIfq0ZKOEHT-jAsjJDzNemC5Pieuq3f0-oHugqcExCitVXK1xv5UBUz6w4_svzZa7UJeTaPacEdm3Kti3WmN459wtC7Sm0tj03DeubrR663cycYBkmrrqWcQYb5wFwO_I6qreABpBEWV3YKPYiWrwSIHNNRNfx73UhOU5AY502Png8uuzArqOK15x9GLo-_Lg5fWg5cR68vTcvplYMgOHk-nUPLyAtCh9AmhyQnit_0MRTBLY9EVU7q7DPTkC16X0Px-JilEDqYt5n2lFqH3Ilh2c6q6_ZTGpnW1-hDWTYqgj_4vXbfArpGnHul5Kzi1K5WkyN3qrFejEcnWWdtxyAYgQmyaviTCOi3E_xqZk2UNhGOUdobmxYWF_0BE6_LZ4RninEWXBmUAMeH-eHGgdo268KJ4IPwbxptYkJdCYgGIQPZ25JPusLKSus2NJsCVmZJO3n4u4j8AKcJ-ChMdCaO9yG_DgnZqvmZtS3DH7qtFWUw5rf8D-5TxM-VNJDn-j85QKO0H52NutYVaF4iY7zJKgC1r36Dw4A5nzm81s2UGVlSBLtFARqu45Z8JxRHnTDil6rzUlmLYuVY9av9iPc3KJfISnodc9fnQpTnkWC7GLR_DRge07lGlV_wrOmC4Ds97tKKg9gv8ab5W57HOI9N6RaUSZUhqGx9VeIz8hlVP4uyK0kkelKORawJRui2EvndV2c167ZvR0xxhNPrvqA728XC7nPScQN2p30KKH8sOlqQV9Nrid8nPBrCWG15RIQ0RSMPzNBQdxGvQUy4C4CtbM0YrHFuOtqMLkAo6k6AgeqpYR0T4cxeGePSBtiHKzV863Se-rfE1fiD-mAzKFKKFK_xwJZHfAQtT6wWs3J5vbDyaVtPnAK28n4yYMgaSy-84lZ6GkHSiPQXe8vFmQDKqPfseJS1kdtpxlFVFghLoAlg6fV4zCG1uNYD4fh4__5GI7hASwUcSKmUHMJxK8iaBkaiwaaL8ugh4MapKEHbtnMcC2MFo4dcmWGZREM8KD-fGtYnWOu_i_TrFgh5iuswQAsHpHnsEGuXmGJv594V0kfwJ1ZUINrEUBgR1SXcSX0TqO-dnDr3_g4oLSkpnEA76mmVePWtWaKbsUd2L1JIZnHGP6W77IHZ3tvViiV_cDnvU7sx8kpZ7uaxqMIWPixHE1xK-lM6-jCDmzwzeciR0BEeH6t1J81FsJh_IQLUbSZ9bXgvNe503BgrHAvmeUYIdfLXllB7wlZo_TyX1hLRLRHBf0OE-BsC7BgGIirhLSdCiOMeL8Xbh49LIR5ZjfCz_MZDPLdQ9sfnWSyL9k0BevUlZLl5mPqRwqRL-FJLq94bnD1GvT63yvaUBAB9zyK-PspeYBHwDfj2nmeWTk_uJ3XPBsGpmxylYaPYSjJOcYXdb8XORmTLOm7PEqJ7yIVVLtWA5rz7tcx4Ezjq9Nx6UCksJbKnrM1K0DzgcwBLu1Axhnyp-hK_pC69raBHFb8x80dmvvpaBq3K-zCPMeTwuiDlDOjvrJYQSToa3YYj6GH3rl_oxl5EIWCvvIeVacmuWWHmz0By0h18uZSY0QF8Q5BkKswmWxQZFXSCzOS5tPWrcbEjffD5vAM0mx-oz2V_b_jtrn7p0FgAr9tVudkQNnnZ4_zPt_aL9pNbGjFCPVuQcOhAMbGjUG4Jn3cBVLoIQa5Bg2NR1bPf5nMc73rnMoNTZ7MG7-q3nCLuqbvFAnQBmuu08KjbPjfrZ_c4FtR_WBY6C70B8bm-lS4gQDpMdeat3tAbLj5OLJvxmkNXqStzPVDsPsBjb-Ft7xqvy19D"  # Remplace par ton token complet
    }

    # proxy_url = "https://proxy.webshare.io/api/v2/proxy/list/download/imbdafrgxzxhlpbkjypmbcbvnhoatmffshqsemkq/-/any/username/direct/-/"
    # proxies_list = fetch_proxy_list(proxy_url)

    # chosen_proxy = random.choice(proxies_list)

    # proxies = {
    #     "http": f"http://ngrguayu:n6rhyptcinnw@{chosen_proxy['ip']}:{chosen_proxy['port']}",
    #     "https": f"http://ngrguayu:n6rhyptcinnw@{chosen_proxy['ip']}:{chosen_proxy['port']}",
    # }

    proxies = {
        "http": f"http://145.223.82.240:3128",
        "https": f"http://145.223.82.240:3128",
    }

    try:
        # Effectuer la requête
        response = requests.get(url, proxies=proxies, headers=headers)
        response.raise_for_status()  # Vérifier si la requête est réussie (code 200)

        if response.status_code == 200:
            data = response.json()
            nb_element = data["total"]
            print(f"Position valide ({x}, {y}). On insère {nb_element} éléments (si ils ne sont pas déjà existants).")



            if nb_element > 0:
                # Connexion à la base de données SQLite
                conn = sqlite3.connect('merged_database_v2.db')
                cursor = conn.cursor()

                max_x = x
                for poi_group in data["data"]:  # Chaque groupe de POI
                    posX = poi_group["posX"]
                    posY = poi_group["posY"]
                    # Récupérer tous les POI pour cette position
                    pois_to_insert = []
                    for poi in poi_group["pois"]:
                        name_fr = poi["name"]["fr"]

                        # Vérification si le POI existe déjà dans la base de données
                        cursor.execute("SELECT 1 FROM points_of_interest WHERE posX = ? AND posY = ? AND name_fr = ? LIMIT 1",
                                       (posX, posY, name_fr))
                        existing_poi = cursor.fetchone()

                        # Si le POI n'existe pas déjà, on l'ajoute à la liste d'insertion
                        if not existing_poi:
                            pois_to_insert.append((posX, posY, name_fr))  # Ajouter les POI à la liste

                    # Insertion dans la base de données après avoir collecté tous les POI non existants
                    if pois_to_insert:
                        print(f"Nouveau Point : {pois_to_insert}" )
                        cursor.executemany("INSERT INTO points_of_interest (posX, posY, name_fr) VALUES (?, ?, ?)",
                                            pois_to_insert)
                        conn.commit()
                        insert = True

                conn.close() # Retourne la coordonnée maximale x rencontrée

            else:
                print(f"Aucun point d'intérêt trouvé pour ({x}, {y}).")

        elif response.status_code == 404:
            print(f"Erreur 404 pour les coordonnées ({x}, {y}) avec direction {direction}. Aucun point d'intérêt trouvé.")

        else:
            print(f"Erreur HTTP {response.status_code} pour les coordonnées ({x}, {y}).")

    except requests.exceptions.RequestException as err:
        print(f"Erreur lors de la requête pour les coordonnées ({x}, {y}) : {err}")
    
    return insert

# Appeler la fonction


if __name__ == "__main__":
    insert = get_treasure_hunt()
    if insert:
        maj_bdd()