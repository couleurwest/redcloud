"""Tests de connexion à Nextcloud et récupération des Decks.

✅ Vérifie la connexion à Nextcloud avec les bonnes identifiants.
✅ Vérifie que l'utilisateur connecté possède un login et un e-mail.
✅ Récupère et affiche les Decks (tableaux de cartes).
"""
import random

import httpx
import pytest
import requests
from httpx import HTTPStatusError
from requests.auth import HTTPBasicAuth

# 🔹 Remplace avec l'URL de ton serveur Nextcloud et tes identifiants
NEXTCLOUD_URL = "https://sft.gcsguyasis.fr/"
USERNAME = "klentin"
PASSWORD = "-$onG0h1n-"
HEADERS = {
    'Content-Type': 'application/json;charset=utf-8',
    'OCS-APIRequest': 'True',
    'Accept': 'application/json'
}


PROJET = {
    'redmine_project' : 'Beloud',
    'issue_title' : 'Montana',
    'description' : """Mais tout ce ci n'est qu'un reve"
    Des bribes de mon passe""",
    "detail": ["Premier jet", "une histoire **sans ombrage**"],
    "status":  ["en cours", "En attente"],
    "category": "test",
    "priority": ["normal", "important"],
    'due_date': None
}

class Nextclouder:
    """Classe pour stocker les infos de l'utilisateur Nextcloud."""
    board = None
    stacks = ""
    labels = {}
    card =None
    
    __URL_USER_CONNEXION = "{}ocs/v2.php/cloud/user?format=json"
    ____URL_USER_BOARDS = "{}index.php/apps/deck/api/v1.0/boards"
    __URL_USER_STACK = "{}index.php/apps/deck/api/v1.0/boards/{}/stacks"
    __URL_USER_LABEL = "{}index.php/apps/deck/api/v1.0/boards/{}/labels"
    __URL_USER_CARD = "{}index.php/apps/deck/api/v1.0/boards/{}/stacks/{}"
    __URL_LABEL_ASSIGN = "{}index.php/apps/deck/api/v1.0/boards/{}/stacks/{}/cards/{}/assignLabel"
    __URL_LABEL_REMOVE = "{}index.php/apps/deck/api/v1.0/boards/{}/stacks/{}/cards/{}/removeLabel"
    __URL_USER_ASSIGN = "{}index.php/apps/deck/api/v1.0/boards/{}/stacks/{}/cards/{}/assignUser"
    __URL_USER_COMMENT = "{}ocs/v2.php/apps/deck/api/v1.0/cards/{}/comments"

    LST_STATUS = [
        ('2', 'In progress','cours'),
        ('3', 'In release','validation'),
        ('1', 'In stand by','attente'),
        ('4', 'Closed','fermé')
    ]

    @classmethod
    async def set_comment(self, client, card_id, message):
        url = Nextclouder.__URL_USER_COMMENT.format(NEXTCLOUD_URL, card_id)
        await self.httpx_requests(client, url, method='POST', params={'message': message})

    @classmethod
    async def assign_label(cls, client:httpx.AsyncClient, nextcloud_board_id, stack_id, card_id, label_id):
        url = Nextclouder.__URL_LABEL_ASSIGN.format(NEXTCLOUD_URL, nextcloud_board_id, stack_id, card_id)
        await cls.httpx_requests(client,url,method='PUT', params={'labelId': label_id})

    @classmethod
    async def remove_label (cls, client, nextcloud_board_id, nextcloud_stack_id, nextcloud_card_id, nextcloud_label_id):
        url = Nextclouder.__URL_LABEL_REMOVE.format(NEXTCLOUD_URL, nextcloud_board_id, nextcloud_stack_id, nextcloud_card_id)

        await cls.httpx_requests(client, url, method='PUT', params={'labelId': nextcloud_label_id})

    @staticmethod
    async def httpx_requests(client, url, method='GET', params=None):

        if method == 'PUT':
            request = await client.put(url, headers=HEADERS, json=params)
        elif method == 'POST':
            request = await client.post(url, headers=HEADERS, json=params)
        elif method == 'DELETE':
            request = await client.delete(url, headers=HEADERS)
        else:
            request = await client.get(url, headers=HEADERS, params=params)

        return request.json() if request.is_success else request.raise_for_status()  # HTTPStatusError

    @classmethod
    async def create_stacks(cls, client:httpx.AsyncClient, nextcloud_board_id):
        url = Nextclouder.__URL_USER_STACK.format(NEXTCLOUD_URL, nextcloud_board_id)

        for statut in Nextclouder.LST_STATUS:
            dcm = {'title': statut[1], 'order': statut[0]}
            await cls.httpx_requests(client, url, method='POST', params=dcm)

    @classmethod
    async def create_label(cls, client:httpx.AsyncClient, nextcloud_board_id, label_title):
        url = Nextclouder.__URL_USER_LABEL.format(NEXTCLOUD_URL, nextcloud_board_id)
        label = {
            "title": label_title,  # Nom de l’étiquette
            "color": "{:06x}".format(random.randint(0, 0xFFFFFF))
        }
        await cls.httpx_requests(client,url, method='POST', params=label)

    @classmethod
    async def find_or_create_board(cls, client: httpx.AsyncClient, board_name: str):
        """CReation d'un board relatif au projet
        redmine_project : Nom du projet"""
        url = Nextclouder.____URL_USER_BOARDS.format(NEXTCLOUD_URL)
        boards = await cls.httpx_requests(client, url, params={'details': True})

        for board in boards:
            if board['title'] == board_name:
                if not board['stacks']:
                    await cls.create_stacks(client,board['id'])
                break
            board = None

        if not board:
            couleur = "{:06x}".format(random.randint(0, 0xFFFFFF))
            data = {"title": board_name, "color": couleur}

            board = await cls.httpx_requests(client, url, method='POST', params=data)
            board_id = board['id']

            await cls.create_stacks(client, board_id)
            board = await cls.httpx_requests(client, url + f'/{board_id}', params={'details': True})

        return board

    @classmethod
    async def delete_label (cls, client, nextcloud_board_id, nextcloud_label_id):
        url = Nextclouder.__URL_LABEL_DELETE.format(NEXTCLOUD_URL, nextcloud_board_id, nextcloud_label_id)

        await cls.httpx_requests(client, url, method='DELETE')

    @classmethod
    async def find_card(cls, client, nextcloud_board_id,  nextcloud_card_title):
        url = Nextclouder.__URL_USER_STACK.format(NEXTCLOUD_URL, nextcloud_board_id)
        stacks = await cls.httpx_requests(client, url)
        for stack in stacks:
            for card in stack['cards']:
                if card['title'] == nextcloud_card_title:
                    return  stack['id'], card

        return None,None

    @classmethod
    async def find_or_create_card(cls, client, nextcloud_board_id, nextcloud_stack_id, nextcloud_card_title,
                                  nextcloud_card_description, nextcloud_card_due_date):

        card_stack_id, card = await cls.find_card(client, nextcloud_board_id,  nextcloud_card_title)
        if card and card_stack_id!= nextcloud_stack_id:
            url = Nextclouder.__URL_USER_CARD.format(NEXTCLOUD_URL, nextcloud_board_id, card_stack_id)
            await cls.httpx_requests(client,  f'{url}/cards/{card['id']}/reorder', method='PUT',  params={'stackId':nextcloud_stack_id, 'order':0 })
        elif card is None:
            url = Nextclouder.__URL_USER_CARD.format(NEXTCLOUD_URL, nextcloud_board_id, nextcloud_stack_id)
            due_date = nextcloud_card_due_date.isoformat() if nextcloud_card_due_date else None
            card = {
                "title": nextcloud_card_title,
                "type": "plain",  # "plain" (texte brut) ou "text/markdown" (formaté)
                "description": nextcloud_card_description,
                "order": 0,
                "duedate": due_date
            }
            card = await cls.httpx_requests(client, f'{url}/cards', method='POST', params=card)

        return card

    @classmethod
    async def assign_user(cls, client: httpx.AsyncClient, nextcloud_board_id, stack_id, card_id, user_id):
        url = Nextclouder.__URL_USER_ASSIGN.format(NEXTCLOUD_URL, nextcloud_board_id, stack_id, card_id)
        try:
            await cls.httpx_requests(client, url, method='PUT', params={'userId': user_id})
        except HTTPStatusError as exs:
            if exs.response.status_code != 400:
                raise exs



@pytest.mark.asyncio
async def test_nextcloud_boards():
    """Test : Vérifier que la connexion à Nextcloud est réussie."""
    labels_id = []
    labels_to_remove = []
    nextcloud_category = PROJET['category']
    nextcloud_priority = PROJET['priority'][0]

    async with httpx.AsyncClient(auth=(USERNAME, PASSWORD), verify=False, base_url=NEXTCLOUD_URL) as client:
        while nextcloud_category or nextcloud_priority or Nextclouder.board is None:
            Nextclouder.board = await Nextclouder.find_or_create_board(client, PROJET['redmine_project'])

            assert Nextclouder.board, 'creation board pof'
            print('1 - Board : OK =>', Nextclouder.board)

            board_id = Nextclouder.board['id']
            nextcloud_stack = Nextclouder.board.pop('stacks')
            print('2 - Stacks : OK =>', nextcloud_stack)

            nextcloud_label = Nextclouder.board.pop('labels') or []
            print('3 - Label : OK =>', nextcloud_label)

            for label in nextcloud_label:
                label_id = label['id']
                if label['title'] == nextcloud_category:
                    labels_id.append(label_id)
                    nextcloud_category = ''
                elif label['title'] == nextcloud_priority:
                    labels_id.append(label_id)
                    nextcloud_priority = ''
                else:
                    labels_to_remove.append(label_id)

            if nextcloud_category:
                await Nextclouder.create_label(client, board_id, nextcloud_category)

            if nextcloud_priority:
                await Nextclouder.create_label(client, board_id, nextcloud_priority)

            for label_id in labels_to_remove:
                Nextclouder.delete_label(client, board_id, label_id)


        print('stacks :', nextcloud_stack)
        Nextclouder.stacks= nextcloud_stack
        print('labels :', nextcloud_label)
        Nextclouder.labels = nextcloud_label


@pytest.mark.asyncio
async def test_nextcloud_card():
    async with httpx.AsyncClient(auth=(USERNAME, PASSWORD), verify=False, base_url=NEXTCLOUD_URL) as client:
        projet_status = PROJET['status'][0]
        stacks = list(filter(lambda status: status[2] in projet_status.lower(), Nextclouder.LST_STATUS))
        stack_name = stacks[0][1] if stacks else 'In stand by'

        stacks = list(filter(lambda stack: stack['title'] == stack_name, Nextclouder.stacks))
        stack_id = stacks[0]['id']

        card = await Nextclouder.find_or_create_card(client, Nextclouder.board['id'],
                                                     stack_id, PROJET['issue_title'],
                                                     PROJET['description'], PROJET['due_date'])
        card_id = card['id']
        for label in Nextclouder.labels:
            await Nextclouder.remove_label(client, Nextclouder.board['id'], stack_id, card_id, label['id'])

        labels_to_assign = list(filter(lambda label: label['title'] in [PROJET['category'],PROJET['priority'][0]],
                                       Nextclouder.labels))
        labels_id = list(map(lambda label: label['id'], labels_to_assign))

        for lid in labels_id:
            await Nextclouder.assign_label(client, Nextclouder.board['id'], stack_id, card_id, lid)

        await Nextclouder.set_comment(client, card_id, PROJET['detail'][0])
        assigned_users = card.get('assignedUsers', [])
        if USERNAME not in assigned_users:
            await Nextclouder.assign_user(client, Nextclouder.board['id'], stack_id, card_id, USERNAME)


@pytest.mark.asyncio
async def test_nextcloud_update():

    nextcloud_priority = PROJET['priority'][0]

    async with httpx.AsyncClient(auth=(USERNAME, PASSWORD), verify=False, base_url=NEXTCLOUD_URL) as client:
        projet_status = PROJET['status'][1]
        stacks = list(filter(lambda status: status[2] in projet_status.lower(), Nextclouder.LST_STATUS))
        stack_name = stacks[0][1] if stacks else 'In stand by'
        stacks = list(filter(lambda stack: stack['title'] == stack_name, Nextclouder.stacks))
        stack_id = stacks[0]['id']

        card = await Nextclouder.find_or_create_card(client, Nextclouder.board['id'],
                                                     stack_id, PROJET['issue_title'],
                                                     PROJET['description'], PROJET['due_date'])
        card_id = card['id']
        for label in Nextclouder.labels:
            await Nextclouder.remove_label(client, Nextclouder.board['id'], stack_id, card_id, label['id'])

        labels_to_assign = list(filter(lambda label: label['title'] in [PROJET['category'],PROJET['priority'][1]],
                                       Nextclouder.labels))
        labels_id = list(map(lambda label: label['id'], labels_to_assign))

        for lid in labels_id:
            await Nextclouder.assign_label(client, Nextclouder.board['id'], stack_id, card_id, lid)

        await Nextclouder.set_comment(client, card_id, PROJET['detail'][1])
        assigned_users = card.get('assignedUsers', [])
        if USERNAME not in assigned_users:
            await Nextclouder.assign_user(client, Nextclouder.board['id'], stack_id, card_id, USERNAME)
