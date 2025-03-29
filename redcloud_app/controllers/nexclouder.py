import random
import httpx
import urllib3
from dreamtools.logmng import CTracker
from httpx import HTTPStatusError


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Nextclouder:
    """
    Classe permettant l'interaction avec Nextcloud Deck, incluant l'authentification et la gestion des cartes.

    :ivar __nextcloud_url: URL du serveur Nextcloud.
    :vartype __nextcloud_url: str
    :ivar __nextcloud_login: Nom d'utilisateur Nextcloud.
    :vartype __nextcloud_login: str
    :ivar __nextcloud_password: Mot de passe de l'utilisateur Nextcloud.
    :vartype __nextcloud_password: str
    :ivar nextcloud_user_id: ID de l'utilisateur authentifié.
    :vartype nextcloud_user_id: str
    """

    HEADERS = {
        "Content-Type": "application/json",
        "OCS-APIRequest": "true",
        "Accept": "application/json"
    }

    __URL_USER_CONNEXION = "ocs/v2.php/cloud/user?format=json"
    __URL_USER_COMMENT = "ocs/v2.php/apps/deck/api/v1.0/cards/{}/comments"
    __URL_USER_BOARDS = "index.php/apps/deck/api/v1.0/boards"
    __URL_USER_STACKS = "index.php/apps/deck/api/v1.0/boards/{}/stacks"
    __URL_USER_LABEL = "index.php/apps/deck/api/v1.0/boards/{}/labels"
    __URL_USER_CARDS = "index.php/apps/deck/api/v1.0/boards/{}/stacks/{}/cards"
    __URL_USER_CARD_REORDER = "index.php/apps/deck/api/v1.0/boards/{}/stacks/{}/cards/{}/reorder"
    __URL_LABEL_ASSIGN = "index.php/apps/deck/api/v1.0/boards/{}/stacks/{}/cards/{}/assignLabel"
    __URL_LABEL_REMOVE = "index.php/apps/deck/api/v1.0/boards/{}/stacks/{}/cards/{}/removeLabel"
    __URL_USER_ASSIGN = "index.php/apps/deck/api/v1.0/boards/{}/stacks/{}/cards/{}/assignUser"
    __URL_LABEL_DELETE = "index.php/apps/deck/api/v1.0/boards/{}/labels/{}"

    LST_STATUS = [
        ('2', 'In progress', 'cours'),
        ('3', 'In release', 'validation'),
        ('1', 'In stand by', 'attente'),
        ('4', 'Closed', 'fermé')
    ]

    def __init__(self, nextcloud_login: str, nextcloud_password: str, nextcloud_url: str):
        """
        Initialise un objet Nextclouder.

        :param nextcloud_login: Nom d'utilisateur Nextcloud.
        :param nextcloud_password: Mot de passe Nextcloud.
        :param nextcloud_url: URL du serveur Nextcloud.
        """
        self.__nextcloud_url = nextcloud_url.rstrip('/')
        self.__nextcloud_login = nextcloud_login
        self.__nextcloud_password = nextcloud_password
        self.nextcloud_user_id = None


    async def httpx_requests(self, client: httpx.AsyncClient, url: str, method: str = 'GET', params: dict = None):
        """
        Effectue une requête HTTP asynchrone avec gestion des erreurs.

        :param client: Client HTTPX asynchrone.
        :param url: URL de la requête.
        :param method: Méthode HTTP ('GET', 'POST', 'PUT', 'DELETE').
        :param params: Paramètres JSON à envoyer dans la requête.
        :return: Réponse JSON ou exception en cas d'échec.
        :raises HTTPStatusError: Si la requête retourne un code d'erreur HTTP.
        """
        if method == 'PUT':
            request = await client.put(url, headers=Nextclouder.HEADERS, json=params)
        elif method == 'POST':
            request = await client.post(url, headers=Nextclouder.HEADERS, json=params)
        elif method == 'DELETE':
            request = await client.post(url, headers=Nextclouder.HEADERS)
        else:
            request = await client.get(url, headers=Nextclouder.HEADERS, params=params)
        return request.json() if request.is_success else request.raise_for_status()  # HTTPStatusError


    def document (self):
        return {
            'nextcloud_url' : self.__nextcloud_url,
            'nextcloud_login' : self.__nextcloud_login,
            'nextcloud_password' : self.__nextcloud_password,
            'nextcloud_user_id' : self.nextcloud_user_id
        }

    @classmethod
    async def login(cls, nextcloud_login: str, nextcloud_password: str, nextcloud_url: str):
        """
        Authentifie un utilisateur Nextcloud et récupère son ID.

        :return: Instance de Nextclouder authentifiée.
        """
        nextcloud_account = cls(nextcloud_login, nextcloud_password, nextcloud_url)
        async with httpx.AsyncClient(auth=(nextcloud_login, nextcloud_password), base_url=nextcloud_url) as client:
            user = await nextcloud_account.httpx_requests(client, cls.__URL_USER_CONNEXION)
            nextcloud_account.nextcloud_user_id = user.get('id', '')

        return nextcloud_account


    async def assign_user(self, client, board_id, stack_id, card_id, user_id):
        """
        Assigne un utilisateur à une carte Deck.

        :param board_id: ID du board Nextcloud.
        :param stack_id: ID du stack où se trouve la carte.
        :param card_id: ID de la carte.
        :param user_id: ID de l'utilisateur à assigner.
        """
        url = self.__URL_USER_ASSIGN.format(board_id, stack_id, card_id)
        try:
            await self.httpx_requests(client, url, method='PUT', params={'userId': user_id})
        except HTTPStatusError as exc:
            if exc.response.status_code != 400:  # 400 = utilisateur déjà assigné
                raise

    async def assign_label(self, client:httpx.AsyncClient, board_id, stack_id, card_id, label_id):
        """
        Assigne un label à une carte.

        :param board_id: ID du board.
        :param stack_id: ID du stack.
        :param card_id: ID de la carte.
        :param label_id: ID du label.
        """
        url = self.__URL_LABEL_ASSIGN.format(board_id, stack_id, card_id)
        await self.httpx_requests(client, url, method='PUT', params={'labelId': label_id})

    async def create_label(self, client: httpx.AsyncClient, board_id, label_title):
        """
        Crée un label pour un board donné.
        :param board_id: ID du board.
        :param label_title: label à créé.
        """
        url = Nextclouder.__URL_USER_LABEL.format(board_id)
        label = {
            "title": label_title,  # Nom de l’étiquette
            "color": "{:06x}".format(random.randint(0, 0xFFFFFF))
        }
        await self.httpx_requests(client, url, method='POST', params=label)

    async def set_comment (self, client:httpx.AsyncClient,card_id,message):
            url = Nextclouder.__URL_USER_COMMENT.format(card_id)
            await self.httpx_requests(client, url, method='POST', params={'message': message})
    async def remove_label (self, client:httpx.AsyncClient, board_id, stack_id, card_id, label_id):
        url = Nextclouder.__URL_LABEL_REMOVE.format( board_id, stack_id, card_id)
        await self.httpx_requests(client, url, method='PUT', params={'labelId': label_id})

    async def delete_label (self, client:httpx.AsyncClient, board_id, label_id):
        url = Nextclouder.__URL_LABEL_DELETE.format( board_id, label_id)
        await self.httpx_requests(client, url, method='DELETE')

    async def create_stacks(self, client:httpx.AsyncClient, board_id):
        url = Nextclouder.__URL_USER_STACKS.format(board_id)

        for statut in Nextclouder.LST_STATUS:
            dcm = {'title': statut[1], 'order': statut[0]}
            await self.httpx_requests(client, url, method='POST', params=dcm)

    async def find_card(self, client:httpx.AsyncClient, nextcloud_board_id, nextcloud_card_title):
        url = Nextclouder.__URL_USER_STACKS.format(nextcloud_board_id)
        stacks = await self.httpx_requests(client, url)
        for stack in stacks:
            print(stack)
            for card in stack.get('cards',[]):
                if card['title'] == nextcloud_card_title:
                    return stack['id'], card

        return None, None

    async def find_or_create_card(self, client:httpx.AsyncClient, board_id, stack_id, card_title, card_description, due_date):
        current_stack_id, card = await self.find_card(client, board_id, card_title)
        if card and current_stack_id != stack_id:
            url = Nextclouder.__URL_USER_CARD_REORDER.format( board_id, current_stack_id, card['id'])
            await self.httpx_requests(client, url, method='PUT', params={'stackId': stack_id, 'order': 0})
        elif card is None:
            due_date = due_date
            card = {
                "title": card_title,
                "type": "plain",  # "plain" (texte brut) ou "text/markdown" (formaté)
                "description": card_description,
                "order": 0,
                "duedate": due_date
            }
            url = Nextclouder.__URL_USER_CARDS.format(board_id, stack_id)
            card = await self.httpx_requests(client, url, method='POST', params=card)

        return card


    async def find_or_create_board(self, client:httpx.AsyncClient, board_name:str):
        """CReation d'un board relatif au projet
        redmine_project : Nom du projet"""
        url = Nextclouder.__URL_USER_BOARDS
        board = None
        boards = await self.httpx_requests(client, url, params={'details':True})

        for board in boards:
            if board['title'] == board_name:
                if not board['stacks']:
                    await self.create_stacks(client, board['id'])
                break
            board = None

        if not board:
            couleur = "{:06x}".format(random.randint(0, 0xFFFFFF))
            data = {"title": board_name, "color": couleur}

            board = await self.httpx_requests(client, url, method='POST', params=data)
            board_id = board['id']

            await self.create_stacks(client, board_id)
            board = await self.httpx_requests(client, url+f'/{board_id}',  params={'details': True})

            for label_id in boards['labels']:
                await self.delete_label(client, board_id, label_id)

        return board

        #On crée l'ensemble des listes/stacks

    async def post_activity(self, project_name, issue_title, issue_description, issue_detail, issue_status,
                            issue_category, issue_priority, due_date):

        async with httpx.AsyncClient(auth=(self.__nextcloud_login, self.__nextcloud_password), verify=False,base_url=self.__nextcloud_url) as client:
            board = None
            labels_id = []
            labels_to_remove = []
            #recheche d'un bord au meme nom que le projet
            CTracker.info_tracking('Update Nextcloud : Gestion board', 'Nextclouder')

            while issue_category or issue_priority or board is None:
                board = await self.find_or_create_board(client, project_name)

                board_id = board['id']
                nextcloud_label = board.pop('labels') or []

                for label in nextcloud_label:
                    label_id = label['id']
                    if label['title'] == issue_category:
                        labels_id.append(label_id)
                        issue_category = ''
                    elif label['title'] == issue_priority:
                        labels_id.append(label_id)
                        issue_priority = ''

                if issue_category:
                    await self.create_label(client, board_id, issue_category)

                if issue_priority:
                    await self.create_label(client, board_id, issue_priority)
            CTracker.info_tracking('Update Nextcloud : Gestion stacks', 'Nextclouder')

            nextcloud_stack = board.pop('stacks')
            stacks_status = list(filter(lambda item: item[2] in issue_status.lower(), Nextclouder.LST_STATUS))
            stack_name = stacks_status[0][1] if stacks_status else 'In stand by'
            stacks = list(filter(lambda stack: stack['title'] ==  stack_name, nextcloud_stack))
            stack_id = stacks[0]['id']

            #nouvelle card
            CTracker.info_tracking('Update Nextcloud : Gestion card', 'Nextclouder')

            card = await self.find_or_create_card(client, board_id, stack_id, issue_title,issue_description, due_date)
            card_id =  card['id']
            CTracker.info_tracking('Update Nextcloud : Gestion Label', 'Nextclouder')
            print(card)
            for lbit in card.get('labels'):
                lbid = lbit['id']
                if lbid in labels_id:
                    labels_id.remove(lbid)
                else:
                    CTracker.info_tracking(f'Update Nextcloud : Remove Label {card_id} {lbid}', 'Nextclouder')
                    await self.remove_label(client, board_id, stack_id,card_id, lbid)

            for lbid in labels_id:
                CTracker.info_tracking('Update Nextcloud : Ajout Label', 'Nextclouder')
                await self.assign_label(client,board_id, stack_id, card_id, lbid)

            CTracker.info_tracking('Update Nextcloud : Gestion comments', 'Nextclouder')
            print(issue_detail)
            await  self.set_comment(client, card_id, issue_detail)

            CTracker.info_tracking('Update Nextcloud : Gestion assigned user', 'Nextclouder')

            if self.nextcloud_user_id not in card.get('assignedUsers'):
                await self.assign_user(client, board['id'], stack_id, card_id,  self.nextcloud_user_id)
