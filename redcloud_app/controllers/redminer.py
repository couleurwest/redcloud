from redminelib import Redmine
from redminelib.exceptions import AuthError, ResourceNotFoundError

from redcloud_app.controllers.authentication import Authentication


class Redminer:
    __redmine_url:str
    __redmine_key:str

    redmine_login: str

    __otp_secret = None
    projects : {}
    issues = {}
    status = []

    def __init__(self, redmine_login, redmine_key, otp_secret):
        self.__redmine_login, self.__redmine_key, self.__otp_secret = redmine_login, redmine_key, otp_secret

    @classmethod
    def signin (cls, redmine_login, redmine_password, redmine_key, redmine_url):
        redmine_client = Redmine(redmine_url, key=redmine_key, requests={"verify": False})
        redmine_user = redmine_client.user.get('current')

        if redmine_user and redmine_user.login == redmine_login:
            config = Authentication.signin(redmine_login, redmine_password, redmine_key, redmine_url)
            engine = Redminer(redmine_login,redmine_url, redmine_key)

        engine = None
    @classmethod
    def login (cls, redmine_login, redmine_password):
        config = Authentication.authenticate_user(redmine_login, redmine_password)
        engine = None

        if config:
            redmine_client = Redmine(config['redmine_url'], key=config['redmine_key'], requests={"verify": False})
            redmine_user = redmine_client.user.get('current')

            if redmine_login != redmine_user.login:
                raise AuthError ("Échec de l'authentification : identifiants non valide")


            engine = Redminer(redmine_login, config['redmine_url'], config['redmine_key'], config['otp_secret'])
            #récupération de toutes les statut de demande
            issues_status = redmine_client.issue_status.all()
            engine.status = [(te.id, te.name) for te in issues_status]

            #récupération de toutes les demande de l'user
            issues = redmine_client.issue.filter(
                assigned_to_id=redmine_user.user_id,
                sort='project_id:asc;due_date:desc',
                status_id='open'
            )
            for issue in issues:
                project = issue.project
                if project.id not in engine.projects:
                    engine.projects[project.id] = {
                        'name': project.name,
                        'categories': [(cat.id, cat.name) for cat in project.issue_categories],
                        'trackers': [(cat.id, cat.name) for cat in project.trackers],
                        'time_entry_activities': [(cat.id, cat.name) for cat in project.time_entry_activities]
                    }

                engine.issues[issue.id] = {
                    'subject': issue.subject,
                    'priority': issue.priority.name,
                    'tracker': (issue.tracker.id, issue.tracker.name),
                    'category': (issue.category.id, issue.category.name) if hasattr(issue, "category") else (),
                    'description': issue.description,
                    'due_date': issue.due_date,
                }
            return engine

    def post_activity (self, issue_id, hours, spent_on, activity_id,  information, status_id=None,
                      done_ratio=None, detail=""):

        redmine_client = Redmine(self.__redmine_url, key=self.__redmine_key, requests={"verify": False})
        redmine_user = redmine_client.user.get('current')

        if status_id:
            params = { 'status_id' : status_id, 'notes' : detail}
            if done_ratio:
                params['done_ratio'] = done_ratio

            if redmine_client.issue.update(issue_id, **params):
                print("✅ Enregistrement de temps réussi")


        if redmine_client.time_entry.create(issue_id,  spent_on=spent_on, hours=hours,
                                                      activity_id=activity_id, user_id=redmine_user.user_id,
                                                      comments=information):
            print("✅ Enregistrement de temps réussi")
