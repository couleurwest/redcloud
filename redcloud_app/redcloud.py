import datetime
from functools import partial

from kivy.properties import StringProperty,  ListProperty

from redcloud_app.controllers import Constantine
from redcloud_app.controllers.authentication import Authentication
from redcloud_app.views.login import LoginScreen
from redcloud_app.views.nextcloud import NextcloudScreen
from redcloud_app.views.otp_auth import OTPSigninScreen, OTPLoginScreen
from redcloud_app.views.signin import SigninScreen

from kivy.app import App
from kivy.core.window import Window

from redcloud_app.views.templates import Background, Title3, CWSimpleText, CWLink
from redcloud_app.views.theme import ThemeDark, ThemeNormal

from kivy.uix.screenmanager import NoTransition
from kivy.uix.screenmanager import ScreenManager

WINDOX_SIZE = (600, 480)

redmine_issues = {
    '520': {
        'category': 'Test et validation',
        'description': 'Validation P2 !!!!',
        'due_date': datetime.date(2025, 1, 28).strftime("%d.%m.%Y"),
        'priority': '1 - Important',
        'project_id': '5',
        'status': "En attente d'information GCS",
        'subject': 'Validation P1-P2',
        'tracker': 'Validation'}, '687': {'category': 'Parametrage et Suivi', 'description': "Bureautique non relier au formulaire\r\nMauvaise association d'actes(commission d'admission)\r\nParametres formulaire incorre...\r\nChamps incorrecte (nom usuel utiliser alors qu'il peut être vide, mauvaise adrese de site, pas de code postal)\r\n\r\n\r\n", 'due_date': datetime.date(2024, 7, 23).strftime("%d.%m.%Y"), 'priority': '0 - Standard', 'project_id': '5', 'status': 'En recettage', 'subject': "Stage d'observation", 'tracker': 'Validation'}, '831': {'category': 'Parametrage et Suivi', 'description': 'Ajouter une alerte portant sur les prescription *non programmé* => Chef de services et directeurs de pole', 'due_date': datetime.date(2024, 10, 4).strftime("%d.%m.%Y"), 'priority': '0 - Standard', 'project_id': '5', 'status': 'En attente de parametrage', 'subject': 'Liste de travail : Alerte prescription', 'tracker': 'Paramétrage'}, '839': {'category': '', 'description': 'Mettre à jours les compétences des PEP Ouest\r\n=> Ressources externes (Pas de PS)\r\n=> Mettre à jour les registres => départ de PS', 'due_date': datetime.date(2024, 11, 22).strftime("%d.%m.%Y"), 'priority': '0 - Standard', 'project_id': '23', 'status': 'Ouvert', 'subject': 'ACTES - Révision les compétences CAMSP', 'tracker': 'Probleme'}, '873': {'category': '', 'description': "\r\n* Vue MDM\r\n* Vacation erroné\r\n* Pas d'accès à la page accueillir\r\n* Parametrage Agenda à réviser\r\n* NavDOssOnglet à reviser\r\n", 'due_date': None, 'priority': '1 - Important', 'project_id': '95', 'status': 'En attente de parametrage', 'subject': 'HM - Parametrage MDM', 'tracker': 'Evolution'}, '885': {'category': '', 'description': 'Formation des agents tous sites confondus (SLM, AWALA)\r\n* Remise à niveau pour les déjà formés 2022\r\n* Prose en main pour les nouveau utilisateurs\r\n', 'due_date': datetime.date(2024, 11, 20).strftime("%d.%m.%Y"), 'priority': '0 - Standard', 'project_id': '20', 'status': 'Planifiée', 'subject': 'Formation I Automne 2024', 'tracker': 'Formation'}, '886': {'category': '', 'description': 'Formation des agents tous sites confondus (SLM, AWALA)\r\n* Prise en main pour les nouveau utilisateurs\r\n', 'due_date': datetime.date(2024, 11, 20).strftime("%d.%m.%Y"), 'priority': '0 - Standard', 'project_id': '20', 'status': 'Planifiée', 'subject': 'Formation II Automne 2024', 'tracker': 'Formation'}, '887': {'category': '', 'description': 'Sensibilisation des nouveaux agents\r\n* Responsabilité individuelle\r\n* RPPS / Identitovigilance', 'due_date': datetime.date(2024, 11, 19).strftime("%d.%m.%Y"), 'priority': '0 - Standard', 'project_id': '20', 'status': 'Planifiée', 'subject': 'E-SANTE : Sensibilisation I ', 'tracker': 'Formation'}, '923': {'category': 'Parametrage et Suivi', 'description': "Problemen d'affichage des résultat de la liste de travail : Infos. à vérifier:", 'due_date': datetime.date(2024, 10, 25).strftime("%d.%m.%Y"), 'priority': '1 - Important', 'project_id': '5', 'status': 'En attente de validation ', 'subject': 'Listes de travail ', 'tracker': 'Probleme'}, '993': {'category': '', 'description': 'La modification des profil dans le cadre de l\'harmonisation du déploiement en prévision de la mise en oeuvre relatif au service CMPP et SESSAD a entrainer des "perte" d\'accès à certaines données. Il faut vérifier les formulaire', 'due_date': datetime.date(2024, 11, 22).strftime("%d.%m.%Y"), 'priority': '0 - Standard', 'project_id': '23', 'status': 'En attente de validation ', 'subject': 'Formulaire - Abonnement', 'tracker': 'Probleme'}, '995': {'category': '', 'description': "Les pc n'accèdent qu'aux dossier qu'à partir de la commission d'admission \r\nVu le 20.11.2024 avec le Medecin", 'due_date': datetime.date(2024, 11, 20).strftime("%d.%m.%Y"), 'priority': '0 - Standard', 'project_id': '23', 'status': 'Ouvert', 'subject': 'Liste de travail - Limitation des PC', 'tracker': 'Evolution DUI'}, '1011': {'category': 'Analyse et Spécifications', 'description': "Analyse du PAP remise par l'ADAPEI\r\nFormatage pour remise SWM\r\n\r\n\r\n", 'due_date': datetime.date(2024, 11, 28).strftime("%d.%m.%Y"), 'priority': '0 - Standard', 'project_id': '5', 'status': 'Ouvert', 'subject': 'Cahier VII - PAP - Bureautique', 'tracker': 'Analyse du besoin'}, '1014': {'category': '', 'description': "Il y a deja des départs, et certains agents n'ont pas ete remis\r\n1 a supprimer\r\n2 a ajouté \r\n\r\nAjouté a la volée pendant la formation. Parametrge a finaliser", 'due_date': datetime.date(2024, 11, 29).strftime("%d.%m.%Y"), 'priority': '1 - Important', 'project_id': '23', 'status': 'En attente de validation ', 'subject': 'Comptes utilisateurs', 'tracker': 'Evolution DUI'}, '1016': {'category': '', 'description': '', 'due_date': datetime.date(2024, 11, 29).strftime("%d.%m.%Y"), 'priority': '1 - Important', 'project_id': '23', 'status': 'Parametrage en cours', 'subject': 'Agenda ', 'tracker': 'Evolution DUI'}, '1051': {'category': 'Parametrage et Suivi', 'description': "La liste des actes au regard des prestations serafin a été fournie. Avant l'envoi a SWM pour paramétrage, nécessité de revue des compétences globale, pour fluidité et lisibilité. ", 'due_date': datetime.date(2025, 1, 13).strftime("%d.%m.%Y"), 'priority': '2 - Urgent', 'project_id': '5', 'status': 'Parametrage en cours', 'subject': 'P5 - Définition des compétences liées aux actes   Paramétrage dans HM', 'tracker': 'Analyse du besoin'}, '1068': {'category': 'Parametrage et Suivi', 'description': 'La parcours à valider\r\n\r\nNotification MDPH > Prise de contact (ViaTrajectoire) > Création du Dossier (avec ou sans rdv) >...ique) > Des trucs (Rien) > Evaluation du besoins > Precription/Bilan > Elabration du PAP = Avenant au contrat (en plus du PAP)', 'due_date': None, 'priority': '1 - Important', 'project_id': '5', 'status': 'Ouvert', 'subject': 'Avenant CAST ', 'tracker': 'Analyse du besoin'}, '1072': {'category': 'Parametrage et Suivi', 'description': "En attendant la planification des formation => Formation de l'administration générale sur le parcours inscription -> Comission d'admission\r\n", 'due_date': datetime.date(2025, 1, 30).strftime("%d.%m.%Y"), 'priority': '0 - Standard', 'project_id': '5', 'status': 'Planifiée', 'subject': "[HM] Formation P3 - Commission d'admission", 'tracker': 'Formation'}, '1077': {'category': 'Parametrage et Suivi', 'description': "Réviser le formulaire d'élaboration du PAP pour l'ESAt uniquement (espace réservé)\r\nAjouter les notion relative à l'avant au CAS, aujourd'hui relié à la commission d'admission", 'due_date': None, 'priority': '1 - Important', 'project_id': '5', 'status': 'En attente de parametrage', 'subject': 'Formulaire & Bureautique', 'tracker': 'Paramétrage'}, '1140': {'category': 'Test et validation', 'description': 'Le formulaire a été conçu en tenant compte du renouvellement du stage d\'observation. Cependant, la commission d\'admission n...aire "Stage d\'observation".\r\n# Mise à jour bureautique :\r\n* Prolongation de stage\r\n* Vérification Convocation de stage ', 'due_date': datetime.date(2025, 2, 17).strftime("%d.%m.%Y"), 'priority': '1 - Important', 'project_id': '5', 'status': 'Parametrage en cours', 'subject': 'Formulaire : Modification', 'tracker': 'Probleme'}}
redmine_projects = {
    '5': {
        'categories': [
            (1, 'Analyse et Spécifications'), (2, 'Parametrage et Suivi'), (3, 'Test et validation')],
        'name': 'ADAPEI',
        'time_entry_activities':
            [(14, 'Parametrage GCS'), (15, 'Parametrage SWM'), (18, 'Recette Parametrage'), (28, 'Analyse et redaction'), (29, 'Point de cadrage GCS-SWM '), (30, 'Accompagnement sur site'), (31, 'Accompagnement en distanciel')],
        'trackers': [(4, 'Evolution DUI'), (5, 'Analyse du besoin'), (6, 'Paramétrage'), (7, 'Validation'), (8, 'Probleme'), (10, 'Formation'), (11, 'Redaction support')]
    }, '20': {'categories': [], 'name': 'POLE OUEST', 'time_entry_activities': [(4, 'Analyse'), (5, 'Développement TU'), (6, 'Recette MOE'), (14, 'Parametrage GCS'), (15, 'Parametrage SWM'), (18, 'Recette Parametrage'), (28, 'Analyse et redaction'), (29, 'Point de cadrage GCS-SWM '), (30, 'Accompagnement sur site'), (31, 'Accompagnement en distanciel')], 'trackers': [(4, 'Evolution DUI'), (5, 'Analyse du besoin'), (6, 'Paramétrage'), (7, 'Validation'), (8, 'Probleme'), (10, 'Formation'), (11, 'Redaction support')]}, '23': {'categories': [], 'name': 'CAMPS TOUPITI', 'time_entry_activities': [(4, 'Analyse'), (5, 'Développement TU'), (6, 'Recette MOE'), (14, 'Parametrage GCS'), (15, 'Parametrage SWM'), (18, 'Recette Parametrage'), (28, 'Analyse et redaction'), (29, 'Point de cadrage GCS-SWM '), (30, 'Accompagnement sur site'), (31, 'Accompagnement en distanciel')], 'trackers': [(4, 'Evolution DUI'), (5, 'Analyse du besoin'), (6, 'Paramétrage'), (7, 'Validation'), (8, 'Probleme'), (10, 'Formation'), (11, 'Redaction support')]}, '95': {'categories': [], 'name': 'PEP OG : Main dans la main', 'time_entry_activities': [(4, 'Analyse'), (5, 'Développement TU'), (6, 'Recette MOE'), (14, 'Parametrage GCS'), (15, 'Parametrage SWM'), (18, 'Recette Parametrage'), (28, 'Analyse et redaction'), (29, 'Point de cadrage GCS-SWM '), (30, 'Accompagnement sur site'), (31, 'Accompagnement en distanciel')], 'trackers': [(1, 'Anomalie'), (2, 'Evolution'), (3, 'Autre demande'), (8, 'Probleme'), (10, 'Formation'), (11, 'Redaction support')]}}
status = [(1, 'Ouvert'), (2, 'En analyse'), (3, 'En arbitrage'), (18, 'En cours de traitement'), (14, 'Priorisation'), (15, 'Planifiée'), (21, 'En développement'), (7, 'A livrer PREPROD'), (20, 'A tester MOE'), (8, 'A tester MOA'), (9, 'A livrer PROD'), (5, 'A corriger'), (6, 'En cours de correction'), (4, 'Annulé'), (10, 'Livré PROD'), (16, 'A valider MOA'), (17, 'A traiter'), (19, 'A valider MOE'), (13, "En attente d'information GCS"), (29, "En attente d'information site"), (28, "En attente d'information SWM"), (22, 'En attente de parametrage'), (23, 'Parametrage en cours'), (26, 'En attente de validation '), (24, 'En recettage'), (25, 'En révision'), (27, 'Livraison Validé'), (11, 'Fermé'), (30, 'Suspendu')]

# Paramètres de la fenêtre
class MainScreen(Background):
    name = "main"# Paramètres de la fenêtre

class IssueDetailScreen(Background):
    """Écran affichant les détails d'une issue."""
    issue_id = StringProperty("")
    issue = StringProperty("")
    project = StringProperty("")
    tracker_category = StringProperty("")
    category = StringProperty("")
    status = StringProperty("")
    priority = StringProperty("")
    description = StringProperty("")
    due_date = StringProperty("")
    time_tracker = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.redmine_status.values= list(map(lambda dl: f'{dl[0] } - {dl[1]}', status))

    def on_enter(self, *args):
        Window.maximize()

    def validation(self):
        redmine_commentaire = self.ids.redmine_commentaire.text
        redmine_activity = self.ids.redmine_activity.selected_value
        redmine_time = self.ids.redmine_time.text
        redmine_date = self.ids.redmine_date.text
        redmine_done_ration = self.ids.redmine_done_ration.text

        for v in [redmine_commentaire, redmine_activity,redmine_time, redmine_date]:
            if not v:
                self.show_message_popup("REmplir les champs obligatoire", "Erreur - données manquantes")
                return False

        try:
            redmine_time = float(redmine_time.trim())  # Vérifie si c'est un nombre et s'il est positif
        except ValueError:
            self.show_message_popup("Valeur temps non valide (0.0)", "Erreur - saisie incorrectes")
            return False

        try:
            redmine_date = redmine_date.trim().replace('.', '-')
            redmine_date = datetime.strptime(redmine_date, "%d-%m-%Y")
        except:
            self.show_message_popup("Date non valide", "Erreur - saisie incorrectes")
            return False

        redmine_note = self.ids.notes.text
        redmine_status = self.ids.redmine_status.selected_value
        redmine_status_id, nextcloud_status = redmine_status.split['-']
        redmine_activity = self.ids.redmine_activity.selected_value
        redmine_activity_id, nextcoud_stick = redmine_activity.split('-')

        Constantine.redmine_account.post_activity(self.issue_id,float(redmine_time), redmine_date, redmine_activity_id.trim(),
                                                  redmine_commentaire, redmine_status_id.trim(), redmine_done_ration, redmine_note)
        nextcloud_deck = self.project
        nextcloud_detail=f"""*{redmine_note}
{redmine_commentaire}"""
        redmine_issue = redmine_issues[self.redmine_issue_id]
        nexcloud_title= redmine_issue['subjet']
        nexcloud_description= redmine_issue['description']
        due_date= redmine_issue['due_date']
        priority= redmine_issue['priority']

        if not redmine_status:
            redmine_status = redmine_issue['status']
        Constantine.nextcloud_account.post_activity(nextcloud_deck, nexcloud_title, nexcloud_description, nextcloud_detail,
                                                    redmine_status,priority,due_date)




class DashScreen(Background):
    name = "dashboard"
    issues_data=[]

    def on_enter(self, **kwargs):
        Window.maximize()


        #redmine_issues = Constantine.redmine_account.issues
        #redmine_projects = Constantine.redmine_account.projects

        self.ids.project_spinner.values = ["Tous les projets"] + list(map(lambda dc: dc['name'], redmine_projects.values()))
        for issue_id , issues in redmine_issues.items():
           project_id = issues['project_id']
           if project_id in redmine_projects:
                self.issues_data.append((f'#{issue_id}', f'[b]{issues["subject"]}[/b]',
                                     redmine_projects[project_id]['name'],
                                     issues['status'], issues['priority'],issues['due_date']))

        self.populate_table()

    def populate_table(self, project_filter="Tous les projets"):
        """Remplit le tableau avec les données filtrées."""
        table = self.ids.table
        table.clear_widgets()

        # Ajouter les en-têtes du tableau
        headers = ["Issue ID", "Nom", "Projet", "Status", "Level", "Due Date"]
        for h in headers:
            table.add_widget(Title3(text=h,halign="center", valign="middle"))

        # Filtrer les données
        filtered_data = [
            issue for issue in self.issues_data if project_filter == "Tous les projets" or issue[2] == project_filter
        ]

        for issue in filtered_data:  # Limite à 20 lignes
            issue_id = issue[0]
            link_issue = CWLink(text=issue_id,size_hint=(1,None))
            link_issue.bind(on_press=partial(self.get_detail, issue_id[1:]))
            table.add_widget(link_issue)

            for value in issue[1:]:
                table.add_widget(CWSimpleText(text=str(value),halign="center", valign="middle",markup=True))

    def get_detail(self, issue_id, instance):
        detail_screen = self.manager.get_screen("issue_detail")
        detail_screen.issue_id = issue_id
        current_issue = redmine_issues[issue_id]
        project = redmine_projects[current_issue['project_id']]

        detail_screen.issue = current_issue['subject']
        detail_screen.project = "Projet " + project["name"]
        detail_screen.tracker_category = current_issue['category'] + ':' + current_issue['tracker']
        detail_screen.priority = current_issue['priority']
        detail_screen.status = current_issue['status']
        detail_screen.description = current_issue['description']
        detail_screen.due_date = current_issue['due_date']
        detail_screen.time_tracker= list(map(lambda dl: f'{dl[0]} - {dl[1]}', project['time_entry_activities']))

        self.manager.current = 'issue_detail'

    def filter_table(self, selected_project):
        """Filtre le tableau en fonction du projet sélectionné."""
        self.populate_table(selected_project)

    def refresh_table(self):
        """Recharge les données du tableau."""
        self.populate_table()

    def open_settings(self):
        """Ouvre les paramètres (fonctionnalité à implémenter)."""
        print("🔧 Ouvrir les paramètres...")




# class Formulaire(BoxLayout):
#     pass
class RCScreenManager(ScreenManager):

    def on_current(self, instance, value):
        """ Change le titre de la fenêtre en fonction de l'écran actif """
        super().on_current(instance, value)

class RedcloudApp(App):
    theme = ThemeNormal()  # Thème par défaut
    # __status = None

    def switch_theme(self, dark_mode):
        """Change le thème entre clair et sombre"""
        self.theme = ThemeDark() if dark_mode else ThemeNormal()

    def build(self):
        self.title = 'Redcloud 3.0'
        self.icon = "visuels/icon.png"

        sm = RCScreenManager()
        sm.transition = NoTransition()

        sm.add_widget(MainScreen(name="main"))
        sm.current = 'main'

        sm.add_widget(OTPSigninScreen(name="otp_signin"))
        sm.add_widget(OTPLoginScreen(name="otp_login"))
        sm.add_widget(SigninScreen(name="signin"))
        sm.add_widget(NextcloudScreen(name="nextcloud"))
        sm.add_widget(LoginScreen(name="login"))

        sm.add_widget(DashScreen(name="dashboard"))
        sm.add_widget(IssueDetailScreen(name="issue_detail"))

        #sm.current = 'login' if Authentication.check_config_file() else 'signin'
        sm.current = 'dashboard'
        return sm


Window.size = WINDOX_SIZE

if __name__ == "__main__":

    #FormsApp().run()
    RedcloudApp().run()
