import toga

from toga.style import Pack
from toga.style.pack import COLUMN, ROW, BOTTOM, CENTER

from redcloud_app.controllers import Constantine
from redcloud_app.views.view_board import BoardScreen
from redcloud_app.views.view_templates import LabelH1, HR, BoxView

ALL_IT='Tous les projet'
class DashScreen(BoxView):
    name = "dashboard"
    issues_data = []
    #

    def __init__(self, *args, **kwargs):
        super().__init__(style=Pack(direction=COLUMN, flex=1), *args,**kwargs)
        self.issues_data = []

        redmine_issues = Constantine.redmine_account.issues
        redmine_projects = Constantine.redmine_account.projects

        self.project_spinner = toga.Selection(items=[ALL_IT] + list(
            map(lambda dc: dc['name'], redmine_projects.values())))
        self.project_spinner.value = ALL_IT
        self.project_spinner.on_change = self.filter_table


        for issue_id, issues in redmine_issues.items():
           project_id = issues['project_id']
           if project_id in redmine_projects:
                self.issues_data.append((f'#{issue_id}', f'[b]{issues["subject"]}[/b]',
                                     redmine_projects[project_id]['name'],
                                     issues['status'], issues['priority'],issues['due_date']))


        self.list_container = toga.Box(style=Pack(direction=COLUMN, gap=10))
        self.scroll_container = toga.ScrollContainer(style=Pack(flex=1))
        self.scroll_container.content = self.list_container

        bottom_bar = toga.Box(style=Pack(direction=ROW, margin=5, align_items="end", flex=0))
        bottom_bar.add(toga.Label("Projets : ", style=Pack(margin=5)))
        bottom_bar.add(self.project_spinner)

        self.add(self.scroll_container)
        self.add(bottom_bar)

        self.populate_list()
        self.main_window.state = toga.constants.WindowState.FULLSCREEN



    def populate_list(self, project_filter=ALL_IT):
        """Remplit le tableau avec les données filtrées."""
        self.scroll_container.content .clear()
        self.list_container.clear()
        # Ajouter les en-têlist_containertes du tableau
        header = toga.Box(style=Pack(direction=ROW, margin=5, gap=5))
        header.add(toga.Label("Issue ID", style=Pack(width=55)))
        header.add(toga.Label('Nom', style=Pack( flex=0.2)))
        header.add(toga.Label("Projet",  style=Pack(flex=0.2)))
        header.add(toga.Label("Level", style=Pack(width=100)))
        header.add(toga.Label("Due Date", style=Pack( width=70)))
        self.list_container.add(header)       # Filtrer les données

        filtered_data = [
            issue for issue in self.issues_data if project_filter == ALL_IT or issue[2] == project_filter
        ]

        for issue in filtered_data:  # Limite à 20 lignes
            issue_id = issue[0]

            row = toga.Box(style=Pack(direction=ROW, gap=15))

            # Création du bouton avec un texte simulant un lien
            uuid_button = toga.Button(issue_id, style=Pack(color="steelblue", text_align=CENTER, width=55))
            uuid_button.on_press = lambda w, uuid_value=issue_id[1:]: self.get_detail(uuid_value)

            row.add(uuid_button)
            row.add(toga.Label(issue[1], style=Pack(flex=0.2)))
            row.add(toga.Label(issue[2], style=Pack(flex=0.2)))
            row.add(toga.Label(issue[3], style=Pack(width=100)))
            row.add(toga.Label(issue[4], style=Pack(width=70)))
            self.list_container.add(row)  # Filtrer les données
        self.list_container. refresh()

    def get_detail(self, issue_id, *args, **kwargs):
        board_view = BoardScreen(self.main_window)
        board_view.populate_screen(issue_id)
        self.main_window.content = board_view

    def filter_table(self, selected_project):
        """Filtre le tableau en fonction du projet sélectionné."""
        selected_project = self.project_spinner.value

        self.populate_list(selected_project)
        self.main_window.content = selected_project
    def refresh_table(self):
        """Recharge les données du tableau."""
        self.populate_list()

    def open_settings(self):
        """Ouvre les paramètres (fonctionnalité à implémenter)."""
        print("🔧 Ouvrir les paramètres...")

