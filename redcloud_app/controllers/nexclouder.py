import random
from typing import Optional

import httpx

import requests
from redminelib.exceptions import AuthError
from requests.auth import HTTPBasicAuth

from redcloud_app.controllers.authentication import Authentication
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Nextclouder:
    """
    Classe permettant l'interaction avec Redmine, incluant l'authentification et la gestion des tickets.

    :ivar __nextcloud_url: URL du serveur Redmine.
    :vartype __nextcloud_url: str
    :ivar __nextcloud_key: Clé API pour l'accès Redmine.
    :vartype __nextcloud_key: str
    :ivar otp_secret: Clé OTP pour la validation en deux étapes.
    :vartype otp_secret: str
    :ivar nextcloud_login: Nom d'utilisateur Redmine.
    :vartype nextcloud_login: str
    :ivar projects: Dictionnaire contenant les projets de l'utilisateur.
    :vartype projects: dict
    :ivar issues: Dictionnaire contenant les demandes assignées à l'utilisateur.
    :vartype issues: dict
    :ivar status: Liste des statuts de demande disponibles.
    :vartype status: list
    """
    HEADERS = {
        "Content-Type": "application/json",
        "OCS-APIRequest": "true"
    }

    __nextcloud_url: str
    __nextcloud_user_id: str
    __nextcloud_login: str
    __nextcloud_password: str

    projects = {}

    __URL_USER_CONNEXION ="{}/ocs/v2.php/cloud/user?format=json"
    ____URL_USER_BOARDS ="{}/index.php/apps/deck/api/v1.0/boards"
    __URL_USER_STACK = "{}/index.php/apps/deck/api/v1.0/boards/{}/stacks"
    __URL_USER_LABEL = "{}/index.php/apps/deck/api/v1.0/boards/{}/labels"
    __URL_USER_CARD = "{}/index.php/apps/deck/api/v1.0/boards/{}/stacks/{}/cards"
    __URL_LABEL_ASSIGN= "{}/index.php/apps/deck/api/v1.0/boards/{}/stacks/{}/cards/{}/assignLabel"
    __URL_LABEL_REMOVE= "{}/index.php/apps/deck/api/v1.0/boards/{}/stacks/{}/cards/{}/removeLabel"
    __URL_LABEL_DELETE= "{}/index.php/apps/deck/api/v1.0/boards/{}/labels/{}"
    __URL_USER_ASSIGN = "{}/index.php/apps/deck/api/v1.0/boards/{}/stacks/{}/cards/{}/assignUser"
    __URL_USER_COMMENT= "{}/ocs/v2.php/apps/deck/api/v1.0/cards/{cardId}/comments"

    LST_STATUS = [
        ('2', 'In progress','cours'),
        ('3', 'In release','validation'),
        ('1', 'In stand by','attente'),
        ('4', 'Closed','fermé')
    ]

    def __init__(self, nextcloud_login: str, nextcloud_password: str,nextcloud_url:str):
        """
        Initialise un objet Nextclouder.

        :param nextcloud_login: Nom d'utilisateur Redmine.
        :param nextcloud_key: Clé API Redmine.
        :param otp_secret: Clé OTP associée à l'utilisateur.
        """
        self.__nextcloud_url = nextcloud_url.rstrip('/')
        self.__nextcloud_login = nextcloud_login
        self.__nextcloud_password = nextcloud_password

    def document (self):
        return {
            'nextcloud_url' : self.__nextcloud_url,
            'nextcloud_login' : self.__nextcloud_login,
            'nextcloud_id' : self.nextcloud_id,
            'nextcloud_password' : self.__nextcloud_password
        }

    async def httpx_requests(self,client, url, method='GET', params=None):

        if method == 'PUT':
            request = await client.put(url, headers=Nextclouder.HEADERS, json=params)
        elif method == 'POST':
            request = await client.post(url, headers=Nextclouder.HEADERS, json=params)
        elif method == 'DELETE':
            request = await client.post(url, headers=Nextclouder.HEADERS)
        else:
            request = await client.get(url, headers=Nextclouder.HEADERS, params=params)

        return request.json() if request.is_success else request.raise_for_status()  # HTTPStatusError

   
    @classmethod
    def login(cls, redmine_login, redmine_password, nextcloud_login: str, nextcloud_password: str,nextcloud_url:str):
        """
        Authentifie un utilisateur via ses identifiants
        """
        nextcloud_account = Nextclouder(nextcloud_login, nextcloud_password, nextcloud_url)
        async with httpx.AsyncClient(auth=(nextcloud_login, nextcloud_password)) as client:
            url = Nextclouder.__URL_USER_CONNEXION.format(nextcloud_url)
            user = nextcloud_account.httpx_request(client, url)
            nextcloud_account.__nextcloud_user_id = user['id']
            Authentication.update_config(redmine_login, redmine_password, **nextcloud_account.document())
            
            return nextcloud_account
        

    async def set_comment (self, client,card_id,message):
        url = Nextclouder.__URL_LABEL_ASSIGN.format(self.__nextcloud_url, card_id)
        await self.httpx_requests(client, url, method='POST', params={'message': message})

    async def assign_user(self, client:httpx.AsyncClient, nextcloud_board_id, stack_id, card_id, user_id):
        url = Nextclouder.__URL_LABEL_ASSIGN.format(self.__nextcloud_url, nextcloud_board_id, stack_id, card_id)
        await self.httpx_requests(client,url,  method='PUT', params={'userId': user_id})
        
    async def assign_label(self, client:httpx.AsyncClient, nextcloud_board_id, stack_id, card_id, label_id):
        url = Nextclouder.__URL_LABEL_ASSIGN.format(self.__nextcloud_url, nextcloud_board_id, stack_id, card_id)
        await self.httpx_requests(client,url,method='PUT', params={'labelId': label_id})

    async def create_label(self, client:httpx.AsyncClient, nextcloud_board_id, label_title):
        url = Nextclouder.__URL_USER_LABEL.format(self.__nextcloud_url, nextcloud_board_id)
        label = {
            "title": label_title,  # Nom de l’étiquette
            "color": "#{:06x}".format(random.randint(0, 0xFFFFFF))
        }
        await self.httpx_requests(client,url, method='POST', params=label)

    async def remove_label (self, client, nextcloud_board_id, nextcloud_stack_id, nextcloud_card_id, nextcloud_label_id):
        url = Nextclouder.__URL_LABEL_REMOVE.format(self.__nextcloud_url, nextcloud_board_id, nextcloud_stack_id, nextcloud_card_id)

        await self.httpx_requests(client, url, method='PUT', params={'labelId': nextcloud_label_id})

    async def delete_label (self, client, nextcloud_board_id, nextcloud_label_id):
        url = Nextclouder.__URL_LABEL_DELETE.format(self.__nextcloud_url, nextcloud_board_id, nextcloud_label_id)

        await self.httpx_requests(client, url, method='DELETE')


    async def find_or_create_card(self, client, nextcloud_board_id, nextcloud_stack_id, nextcloud_card_title,
                          nextcloud_card_description, nextcloud_card_due_date):
        url = Nextclouder.__URL_USER_CARD.format(self.__nextcloud_url, nextcloud_board_id, nextcloud_stack_id)

        stack = await self.httpx_requests(client, url)

        if 'cards' in stack:
            for card in stack['cards']:
                if card['title'] == nextcloud_card_title:
                    break

        if card is None:
            due_date = nextcloud_card_due_date.isoformat() if nextcloud_card_due_date else None
            card = {
                "title": nextcloud_card_title,
                "type": "text/markdown",  # "plain" (texte brut) ou "text/markdown" (formaté)
                "description": nextcloud_card_description,
                "order": 0,
                "duedate": due_date
            }
            card = await self.httpx_requests(client, url, method='POST', params=card)

        return card

    async def create_stacks(self, client:httpx.AsyncClient, nextcloud_board_id):
        url = Nextclouder.__URL_USER_STACK.format(self.__nextcloud_url, nextcloud_board_id)

        for statut in Nextclouder.list_statut:
            dcm = {'title': statut[1], 'order': statut[0]}
            self.httpx_requests(client, url, dcm)

    async def find_or_create_board(self, client:httpx.AsyncClient, board_name:str):
        """CReation d'un board relatif au projet
        redmine_project : Nom du projet"""
        url = Nextclouder.____URL_USER_BOARDS.format(self.__nextcloud_url)
        boards = await self.httpx_requests(client, url, params={'details':True}) or []

        for board in boards:
            if board['title'] == board_name:
                break
            board = None

        if not board:
            couleur = "#{:06x}".format(random.randint(0, 0xFFFFFF))
            data = {"title": board_name, "color": couleur}

            board = await self.httpx_requests(client, url, method='POST', params=data)
            board_id = board['id']

            await self.create_stacks(client, board_id)
            board = await self.httpx_requests(client, url+f'/{board_id}',  params={'details': True})

        return board

        #On crée l'ensemble des listes/stacks

    async def post_activity(self, project_name, issue_title, nextcloud_description, nextcloud_detail, nextcloud_status, nextcloud_category, priority, due_date):

        async with httpx.AsyncClient(auth=(self.nextcloud_login, self.nextcloud_password)) as client:
            board = None
            labels_id = []
            labels_to_remove = []

            #recheche d'un bord au meme nom que le projet
            while nextcloud_category or priority or board is None:
                board = await self.find_or_create_board(client, project_name)
                board_id = board['id']
                nextcloud_stack = board.pop('stacks') or []
                nextcloud_label = board.pop('labels') or []

                for label in nextcloud_label:
                    label_id = label['id']
                    if label['title'] == nextcloud_category:
                        labels_id.append(label_id)
                        nextcloud_category = ''
                    elif label['title'] == priority:
                        labels_id.append(label_id)
                        priority = ''
                    else:
                        labels_to_remove.append(label_id)

                if nextcloud_category:
                    await self.create_label(client, board_id, nextcloud_category)

                if priority:
                    await self.create_label(client, board_id, priority)


            stacks = list(filter(lambda status: status[2] in nextcloud_status.lower() , Nextclouder.LST_STATUS))
            stack_name = stacks[0][1] if stacks else 'In stand by'

            stacks = list(filter(lambda stack: stack['title'] ==  stack_name, nextcloud_stack)),
            stack_id = stacks['id']

            #nouvelle card
            card = await self.find_or_create_card(client, board_id, stack_id, issue_title,
                          nextcloud_description, due_date)
            card_id =  card['id']

            if card['labels']:
                for labels_id in card['labels']:
                    await self.remove_label(client, board_id, stack_id,card_id, labels_id)

            labels_id = list(filter(map(lambda : label['title'] in [nextcloud_category, priority], nextcloud_label)))
            for label in labels_id:
                await self.assign_label(client,board_id, stack_id, card_id, label['id'])

            await  self.set_comment(client, card_id, nextcloud_detail)
            assigned_users = card.get('assignedUsers', [])
            if self.nextcloud_login not in assigned_users:
                await assigned_users
