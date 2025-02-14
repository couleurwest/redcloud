"""Tests de connexion à Nextcloud et récupération des Decks.

✅ Vérifie la connexion à Nextcloud avec les bonnes identifiants.
✅ Vérifie que l'utilisateur connecté possède un login et un e-mail.
✅ Récupère et affiche les Decks (tableaux de cartes).
"""

import pytest
import requests
from requests.auth import HTTPBasicAuth

from tests.test_redmine import redmine_client

# 🔹 Remplace avec l'URL de ton serveur Nextcloud et tes identifiants
NEXTCLOUD_URL = "https://sft.gcsguyasis.fr/"
USERNAME = "klentin"
PASSWORD = "-$onG0h1n-"
HEADERS = {
    "Content-Type": "application/json",
    "OCS-APIRequest": "true"
}


class NcUser:
    """Classe pour stocker les infos de l'utilisateur Nextcloud."""
    pseudo = ""
    email = ""
    decks = {}
    created_stack=None
    created_deck=None
    created_card=None

@pytest.fixture
def nextcloud_client():
    """Fixture pour établir la connexion à Nextcloud."""
    session = requests.Session()
    session.auth = HTTPBasicAuth(USERNAME, PASSWORD)
    return session


def test_nextcloud_connection(nextcloud_client):
    """Test : Vérifier que la connexion à Nextcloud est réussie."""
    url = f"{NEXTCLOUD_URL}/ocs/v2.php/cloud/user?format=json"
    response = nextcloud_client.get(url, headers=HEADERS)
    assert response.status_code == 200, "❌ Échec de la connexion à Nextcloud"

    user_data = response.json()["ocs"]["data"]

    assert "id" in user_data, "L'utilisateur doit avoir un ID"
    assert "email" in user_data, "L'utilisateur doit avoir un e-mail"

    NcUser.pseudo = user_data["id"]
    NcUser.email = user_data["email"]

    print(f"✅ Connexion réussie : {NcUser.pseudo} ({NcUser.email})")


def test_nextcloud_get_decks(nextcloud_client):
    """Test : Vérifier la récupération des Decks de l'utilisateur."""
    url = f"{NEXTCLOUD_URL}/index.php/apps/deck/api/v1.0/boards"
    response = nextcloud_client.get(url)

    assert response.status_code == 200, "❌ Impossible de récupérer les Decks"

    decks = response.json()
    assert len(decks) > 0, "L'utilisateur n'a aucun Deck"

    for deck in decks:
        NcUser.decks[deck["id"]] = {
            "title": deck["title"],
            "shared": deck["shared"],
            "archived": deck["archived"],
        }
        if deck["title"]== "Test Deck" and deck["archived"] ==False:
            NcUser.created_deck = deck["id"]
            print("Deck " + deck['title'])

    print(f"✅ {len(NcUser.decks)} Decks récupérés :", NcUser.decks)


    
def test_create_deck(nextcloud_client):
    """Test : Créer un deck (tableau) dans Nextcloud"""
    url = f"{NEXTCLOUD_URL}/index.php/apps/deck/api/v1.0/boards"
    data = {"title": "Test Deck",    "color": "ffffff"}

    response = nextcloud_client.get(url, headers=HEADERS)
    assert response.status_code == 200, f"Échec de la création du deck ({response.status_code})"

    if not NcUser.created_deck :
        response = nextcloud_client.post(url, headers=HEADERS, json=data)

        assert response.status_code == 200, f"Échec de la création du deck ({response.status_code})"

        deck = response.json()
        NcUser.created_deck = deck["id"]

        print(f"✅ Deck créé avec ID : {NcUser.created_deck}")
        

def test_create_list(nextcloud_client):
    """Test : Ajouter une liste 'Réussite' dans le deck"""
    url = f"{NEXTCLOUD_URL}/index.php/apps/deck/api/v1.0/boards/{NcUser.created_deck}/stacks"

    response = nextcloud_client.get(url, headers=HEADERS)
    assert response.status_code == 200, f"Échec de la création du deck ({response.status_code})"

    deck = response.json()

    if deck:
        deck = deck.pop()
        NcUser.created_stack = deck["id"]
        print("Deck " + deck['title'])
    elif not NcUser.created_stack:
        data = {"title": "Réussite", "order": 1}
        response = nextcloud_client.post(url, headers=HEADERS, json=data)
        assert response.status_code == 200, f"Échec de la création du task ({response.status_code})"
        stack = response.json()
        NcUser.created_stack = stack['id']
        print(f"✅ Liste 'Réussite' créée avec ID : {stack['id']}")

    else:
        response = nextcloud_client.get(url+ f'/{NcUser.created_stack}', headers=HEADERS)
        assert response.status_code == 200, f"Échec de la recuperation du task ({response.status_code})"
        stack = response.json()
        if stack['cards']:
            NcUser.created_card = stack['cards'] [0] ['id']

def test_create_card(nextcloud_client):
    """Test : Ajouter une liste 'Réussite' dans le deck"""
    url = f"{NEXTCLOUD_URL}/index.php/apps/deck/api/v1.0/boards/{NcUser.created_deck}/stacks/{NcUser.created_stack}/cards"

    #2019-12-24T19:29:30+00:00
    if not NcUser.created_card:
        data = {"title": "ma permier card", "type": "plain", "order":1, 'description': "la vie de rever", "duedate":None}
        response = nextcloud_client.post(url, headers=HEADERS, json=data)
        if response.status_code == 200:
            card = response.json()
            NcUser.created_card = card['id']

        assert NcUser.created_stack, f"Échec de la création du task ({response.status_code})"
    else:
        data = {"title": "tonio montana", "type": "plain", "order":1, 'description': "la vie de rever", "duedate":None}
        response = nextcloud_client.put(url+ f'/{NcUser.created_card}', headers=HEADERS , json=data)

        assert response.status_code == 200, f"Échec de la recuperation du task ({response.status_code})"

    print(f"✅ Liste 'Réussite' créée avec ID : {NcUser.created_card}")