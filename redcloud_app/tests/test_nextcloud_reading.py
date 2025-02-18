"""Tests de connexion à Nextcloud et récupération des Decks.

✅ Vérifie la connexion à Nextcloud avec les bonnes identifiants.
✅ Vérifie que l'utilisateur connecté possède un login et un e-mail.
✅ Récupère et affiche les Decks (tableaux de cartes).
"""
import httpx
import pytest
import requests
from requests.auth import HTTPBasicAuth

# 🔹 Remplace avec l'URL de ton serveur Nextcloud et tes identifiants
NEXTCLOUD_URL = "https://sft.gcsguyasis.fr"
USERNAME = "klentin"
PASSWORD = "-$onG0h1n-"
HEADERS = {
    "Content-Type": "application/json",
    "OCS-APIRequest": "true"
}


class NcUser:
    """Classe pour stocker les infos de l'utilisateur Nextcloud."""
    user_id = ""
    email = ""
    boards = []
    stack = []
    cards = []
    created_stack = None
    created_deck = None
    created_card = None




async def httpx_requests(client, url, post=None, params=None):

    if post:
        request = await client.post(url, headers=HEADERS, json=post)
    else:
        request = await client.get(url, headers=HEADERS, params=params)

    return request.json()  if request.is_success else request.raise_for_status() #HTTPStatusError

async def httpx_delete(client, url, put=None):
    if put:
        request = await client.put(url, headers=HEADERS, json=put)
    else:
        request = await client.delete(url, headers=HEADERS)

    return request.json()  if request.is_success else request.raise_for_status()

@pytest.mark.asyncio
async def test_nextcloud_connection():
    """Test : Vérifier que la connexion à Nextcloud est réussie."""
    url = f"{NEXTCLOUD_URL}/ocs/v2.php/cloud/user?format=json"

    async with httpx.AsyncClient(auth=(USERNAME, PASSWORD)) as client:
        respons_json = await httpx_requests(client,url)

    user_data = respons_json["ocs"]["data"]

    assert "id" in user_data, "L'utilisateur doit avoir un ID"
    assert "email" in user_data, "L'utilisateur doit avoir un e-mail"

    NcUser.user_id = user_data["id"]

    print(f"✅ Connexion réussie :" ,user_data)


@pytest.mark.asyncio
async def test_nextcloud_board():
    """Test : Vérifier la récupération des Decks de l'utilisateur."""
    url = f"{NEXTCLOUD_URL}/index.php/apps/deck/api/v1.0/boards"
    async with httpx.AsyncClient(auth=(USERNAME, PASSWORD)) as client:
        decks = NcUser.boards = await httpx_requests(client,url, params={'details':True})

    assert len(decks) > 0, "L'utilisateur n'a aucun Deck"

    board = decks[0] if decks else 'nop'

    print(f"✅ {len(NcUser.boards)} Decks récupérés :")
    print('stacks :', board['stacks'] )
    print('label :', board['labels'] )
    print('users :', board['users'] )

@pytest.mark.asyncio
async def test_nextcloud_cards():
    """Test : Vérifier la récupération des Decks de l'utilisateur."""
    if NcUser.boards:
        board = NcUser.boards[0]
        board_id = board['id']
        for stack in board['stacks']:
            stack_id = stack['id']

            url = f"{NEXTCLOUD_URL}/index.php/apps/deck/api/v1.0/boards/{board_id}/stacks/{stack_id}"

            async with httpx.AsyncClient(auth=(USERNAME, PASSWORD)) as client:
                stack = await httpx_requests(client, url, params={'details':True})

                if 'cards' in stack:
                    NcUser.cards = stack['cards']
                    break


        print(f"✅ {len(NcUser.cards)} Card récupérés :", NcUser.cards)

@pytest.mark.asyncio
async def test_nextcloud_card():
    """Test : Vérifier la récupération des Decks de l'utilisateur."""
    url = f"{NEXTCLOUD_URL}/index.php/apps/deck/api/v1.0/boards/16/stacks/43/cards/64"

    async with httpx.AsyncClient(auth=(USERNAME, PASSWORD)) as client:
        card = await httpx_requests(client, url)

        print(f"✅ Card récupérée :", card)

