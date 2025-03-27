from redminelib import Redmine
from redminelib.exceptions import AuthError

from redcloud_app.controllers.authentication import Authentication
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Redminer:
    """
    Classe permettant l'interaction avec Redmine, incluant l'authentification et la gestion des tickets.

    :ivar __redmine_url: URL du serveur Redmine.
    :vartype __redmine_url: str
    :ivar __redmine_key: Clé API pour l'accès Redmine.
    :vartype __redmine_key: str
    :ivar otp_secret: Clé OTP pour la validation en deux étapes.
    :vartype otp_secret: str
    :ivar redmine_login: Nom d'utilisateur Redmine.
    :vartype redmine_login: str
    :ivar projects: Dictionnaire contenant les projets de l'utilisateur.
    :vartype projects: dict
    :ivar issues: Dictionnaire contenant les demandes assignées à l'utilisateur.
    :vartype issues: dict
    :ivar status: Liste des statuts de demande disponibles.
    :vartype status: list
    """

    __redmine_url: str
    __redmine_key: str

    otp_secret = None

    redmine_login: str
    redmine_password: str

    email: str

    projects = {}
    issues = {}
    status = []
    journals = []

    def __init__(self, redmine_login: str, redmine_password: str,redmine_url: str, redmine_key: str,otp_secret: str):
        """
        Initialise un objet Redminer.

        :param redmine_login: Nom d'utilisateur Redmine.
        :param redmine_key: Clé API Redmine.
        :param otp_secret: Clé OTP associée à l'utilisateur.
        """
        self.redmine_login, self.__redmine_key,self.redmine_password, self.otp_secret = (
            redmine_login, redmine_key,redmine_password, otp_secret)
        self.__redmine_url = redmine_url

    @classmethod
    def signin(cls, redmine_login: str, redmine_password: str, redmine_key: str, redmine_url: str):
        """
        Inscription d'un utilisateur dans le système avec création de la clé OTP.

        :param redmine_login: Nom d'utilisateur Redmine.
        :param redmine_password: Mot de passe pour la sécurisation du fichier.
        :param redmine_key: Clé API Redmine.
        :param redmine_url: URL du serveur Redmine.
        :return: Instance de Redminer si l'inscription est réussie, sinon None.
        """

        if  Authentication.check_config_file():
            raise FileExistsError ('Un compte a ete configurer pour ce poste')

        redmine_client = Redmine(redmine_url, key=redmine_key, requests={"verify": False})
        redmine_user = redmine_client.user.get('current')

        if redmine_user and redmine_user.login == redmine_login:
            return Redminer(redmine_login, redmine_password, redmine_url, redmine_key, None)

        raise AuthError("Échec de l'authentification : identification impossible")

    @classmethod
    def login(cls, redmine_login: str, redmine_password: str):
        """
        Authentifie un utilisateur via ses identifiants et récupère ses tickets et statuts.

        :param redmine_login: Nom d'utilisateur Redmine.
        :param redmine_password: Mot de passe pour déchiffrer les données stockées.
        :raises AuthError: En cas d'échec d'authentification.
        :return: Instance de Redminer avec les données de l'utilisateur.
        """
        if not Authentication.check_config_file():
            raise FileNotFoundError ('Le fichier n\'existe pas')

        config = Authentication.authenticate_user(redmine_login, redmine_password)

        if config:
            redmine_client = Redmine(config['redmine_url'], key=config['redmine_key'], requests={"verify": False})
            redmine_user = redmine_client.user.get('current')

            if redmine_login != redmine_user.login:
                raise AuthError()

            redmine_account = Redminer(redmine_login, redmine_password,  config['redmine_url'], config['redmine_key'],config['otp_secret'])

            # Récupération des statuts de tickets
            issues_status = redmine_client.issue_status.all()
            redmine_account.status = [(status.id, status.name) for status in issues_status]

            # Récupération des tickets assignés à l'utilisateur
            issues = redmine_client.issue.filter(
                assigned_to_id=redmine_user.id,
                sort='project_id:asc;due_date:desc',
                status_id='open', include=['journals']
            )

            for issue in issues:
                project = issue.project
                if project.id not in redmine_account.projects:
                    redmine_account.projects[project.id] = {
                        'name': project.name,
                        'categories': [(cat.id, cat.name) for cat in project.issue_categories],
                        'trackers': [(cat.id, cat.name) for cat in project.trackers],
                        'time_entry_activities': [(act.id, act.name) for act in project.time_entry_activities]
                    }

                redmine_account.issues[issue.id] = {
                    'subject': issue.subject,
                    'project_id': project.id,
                    'priority': issue.priority.name,
                    'tracker':  issue.tracker.name,
                    'status': issue.status.name,
                    'category': issue.category.name if hasattr(issue, "category") else '',
                    'description': issue.description,
                    'due_date': issue.due_date.strftime("%d.%m.%Y") if  issue.due_date else '',
                    'journals': [ journal.notes for journal in issue.journals if journal.notes][-3:]  # Prendre les
                }

                nextcloud_account= {
                    'nextcloud_url': config['nextcloud_url'],
                    'nextcloud_login': config['nextcloud_login'],
                    'nextcloud_password': config['nextcloud_password']
                } if config.get('nextcloud_login') else None

            return redmine_account, nextcloud_account

        raise AuthError("Échec de l'authentification : identifiants non valides")

    def post_activity(self, issue_id: int, hours: float, spent_on: str, activity_id: int,
                      commentaire: str, status_id: int = None, note: str = "", done_ratio: int = None):
        """
        Enregistre une activité (temps passé) sur un ticket et peut mettre à jour son statut.

        :param issue_id: Identifiant du ticket concerné.
        :param hours: Nombre d'heures passées.
        :param spent_on: Date de l'entrée de temps.
        :param activity_id: Identifiant de l'activité.
        :param commmentaire: Commentaire sur l'entrée de temps.
        :param status_id: (Optionnel) Nouveau statut du ticket.
        :param done_ratio: (Optionnel) Progression du ticket en pourcentage.
        :param note: (Optionnel) Notes supplémentaires.
        """
        redmine_client = Redmine(self.__redmine_url, key=self.__redmine_key, requests={"verify": False})
        redmine_user = redmine_client.user.get('current')

        # Mise à jour du statut du ticket
        if status_id:
            params = {'status_id': status_id, 'notes': note}
            if done_ratio:
                params['done_ratio'] = done_ratio

            if redmine_client.issue.update(issue_id, **params):
                print("✅ Mise à jour du statut réussie.")

        # Enregistrement du temps passé
        if redmine_client.time_entry.create(issue_id, spent_on=spent_on, hours=hours,
                                            activity_id=activity_id, user_id=redmine_user.id,
                                            comments=commentaire):
            print("✅ Enregistrement du temps réussi.")

    def document (self):
        return  {
                "login": self.redmine_login,
                "redmine_url": self.__redmine_url,
                "redmine_key": self.__redmine_key,
                "otp_secret": self.otp_secret
            }