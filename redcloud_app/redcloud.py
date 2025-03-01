import datetime
from functools import partial

from kivy.properties import StringProperty,  ListProperty

from redcloud_app.controllers import Constantine
from redcloud_app.controllers.authentication import Authentication
from redcloud_app.controllers.toolbox import spilt_uuid
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
# Paramètres de la fenêtre
class MainScreen(Background):
    name = "main"# Paramètres de la fenêtre

class IssueDetailScreen(Background):
    """Écran affichant les détails d'une issue."""
    issue_id = StringProperty("")       #identitifant de ma demande
    issue = StringProperty("")          #titre de la demande
    project = StringProperty("")        #Nom du projet
    tracker_category = StringProperty("")   #Category : tracker
    category = StringProperty("")   #Category : tracker
    priority = StringProperty("")       # priorite
    state = StringProperty("")          # Etat du ticket
    description = StringProperty("")    # DEscription de la demande
    due_date = StringProperty("")       # date de livraison
    activities = ListProperty()          #Listes des activites
    status = ListProperty()             #Listes des statuts
    journals = ListProperty("")
    def on_enter(self, *args):
        Window.maximize()
        self.ids.journals.clear_widgets()
        # Ajouter les nouvelles données sous forme de labels
        for item in self.journals:
            self.ids.journals.add_widget(CWSimpleText(text=item))

    def previous_screen (self):
        self.manager.current = 'dashboard'
        
    def validation(self):
        try:
            redmine_commentaire = self.ids.redmine_commentaire.text.strip()
            redmine_activity = self.ids.redmine_activity.selected_value.strip()
            redmine_date = self.ids.redmine_date.text.strip()
            redmine_time = self.ids.redmine_time.text.strip()

            for v in [redmine_commentaire, redmine_activity,redmine_time, redmine_date]:
                if not v:
                   raise ValueError()

            redmine_time = float(redmine_time)  # Vérifie si c'est un nombre et s'il est positif

            redmine_date = redmine_date.strip().replace('.', '-').replace('/', '-')
            spent_on = datetime.datetime.strptime(redmine_date, "%d-%m-%Y")
        except Exception as ex:
            self.show_message_popup("Vérifiez les données saisie\n" + ex.__str__(), "Erreur - saisie incorrectes")
            return False

        redmine_note =  self.ids.redmine_note.text.strip()
        redmine_status = self.ids.redmine_status.selected_value
        redmine_status_id, redmine_status = spilt_uuid(redmine_status) if redmine_status else None
        redmine_activity_id, redmine_activity = spilt_uuid(redmine_activity)

        _, priority= spilt_uuid(self.priority)

        print("nextcloud_account.post_activity (", self.project, self.issue, self.description, f'*{redmine_commentaire}*\n{redmine_note}',
              redmine_status, self.category, priority, self.due_date, ')')
        print("redmine_account.post_activity (", self.issue_id, redmine_time, spent_on, redmine_activity_id, redmine_commentaire,
                                                  redmine_status_id, redmine_note, ')')
        #Constantine.nextcloud_account.post_activity(self.project, self.issue, self.description,
        #                                            f'*{redmine_commentaire}*\n{redmine_note}',
        #                                            redmine_status, self.category,priority, self.due_date)

        #Constantine.redmine_account.post_activity(self.issue_id, redmine_time, spent_on, redmine_activity_id, redmine_commentaire,
        #                                          redmine_status_id, redmine_note, done_ratio=10)




class DashScreen(Background):
    name = "dashboard"
    issues_data = []

    def on_enter(self, **kwargs):
        Window.maximize()

        redmine_issues = Constantine.redmine_account.issues
        redmine_projects = Constantine.redmine_account.projects

        self.ids.project_spinner.values = ["Tous les projets"] + list(
            map(lambda dc: dc['name'], redmine_projects.values()))
        for issue_id, issues in redmine_issues.items():
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
        redmine_account = Constantine.redmine_account
        redmine_issues = redmine_account.issues
        redmine_projects = redmine_account.projects
        redmine_status = redmine_account.status

        detail_screen: IssueDetailScreen = self.manager.get_screen("issue_detail")
        detail_screen.issue_id = issue_id

        current_issue = redmine_issues[int(issue_id)]
        project = redmine_projects[current_issue['project_id']]

        detail_screen.project = "Projet " + project["name"]
        detail_screen.issue = current_issue['subject']
        detail_screen.category = current_issue['category'] or ''
        detail_screen.tracker_category = current_issue['category'] + ' : ' if current_issue['category'] else ' '  + current_issue['tracker']
        detail_screen.priority = current_issue['priority']
        detail_screen.state = current_issue['status']
        detail_screen.description = current_issue['description']
        detail_screen.due_date = current_issue['due_date']
        detail_screen.activities= list(map(lambda dl: f'{dl[0]} - {dl[1]}', project['time_entry_activities']))
        detail_screen.status = list(map(lambda dl: f'{dl[0] } - {dl[1]}', redmine_status))
        detail_screen.journals =  current_issue['journals']


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

        sm.current = 'login' if Authentication.check_config_file() else 'signin'
        #sm.current = 'dashboard'
        return sm


Window.size = WINDOX_SIZE

if __name__ == "__main__":

    #FormsApp().run()
    RedcloudApp().run()
