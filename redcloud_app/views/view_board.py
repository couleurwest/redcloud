import asyncio

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER

from redcloud_app.controllers import Constantine
from redcloud_app.controllers.toolbox import spilt_uuid
from redcloud_app.views import widget_date
from redcloud_app.views.color_palette import ColorPalette
from redcloud_app.views.view_templates import LabelH2, HR, BoxView, LabelH3


class BoardScreen(BoxView):
    issue_id: str = ''  # identitifant de ma demande
    issue: str = ''  # titre de la demande
    project: str = ''  # Nom du projet
    tracker_category: str = ''  # Category : tracker
    category: str = ''  # Category : tracker
    priority: str = ''  # priorite
    state: str = ''  # Etat du ticket
    description: str = ''  # DEscription de la demande
    due_date: str = ''  # date de livraison
    activities = []
    status = []
    journals = []

    def __init__(self, *args, **kwargs):
        self.issue_time_tracked = None
        self.issue_date = None
        self.issue_status = None
        self.commentaire = None
        self.journal_note = None
        self.issue_activities = None

        super().__init__(style=Pack(direction=COLUMN, flex=1, margin=5, gap=5), *args, **kwargs)

    def populate_screen(self, issue_id):
        while self.children:
            self.remove(self.children[0])

        redmine_account = Constantine.redmine_account
        redmine_issues = redmine_account.issues
        current_issue = redmine_issues[int(issue_id)]
        redmine_status = redmine_account.status

        redmine_projects = redmine_account.projects
        project = redmine_projects[current_issue['project_id']]

        header = toga.Box(style=Pack(direction=ROW, gap=5))
        v = f"#{issue_id}-" + project["name"]
        header.add(LabelH2(v, color=ColorPalette.PRIMARY, flex=0.3))
        header.add(LabelH2("Catégorie", flex=0.2, color=ColorPalette.ACCENT))
        header.add(LabelH2("Tracker", flex=0.2, color=ColorPalette.ACCENT))
        header.add(LabelH2("Priorité", flex=0.2, color=ColorPalette.ACCENT))
        header.add(LabelH2("Statut", flex=0.1, color=ColorPalette.ACCENT))
        self.add(header)
        header = toga.Box(style=Pack(direction=ROW, gap=5))
        header.add(LabelH3(current_issue['subject'], flex=0.3, color=ColorPalette.ACCENT))
        header.add(LabelH3(current_issue.get('category', ''), flex=0.2, color=ColorPalette.SECONDARY))
        header.add(LabelH3(current_issue.get('tracker', ''), flex=0.2, color=ColorPalette.SECONDARY))
        v = current_issue.get('due_date', '')
        header.add(LabelH3(current_issue['priority'] + f' [{v}]', flex=0.2, color=ColorPalette.SECONDARY))
        header.add(LabelH3(current_issue['status'], flex=0.1, color=ColorPalette.SECONDARY))
        self.add(header)

        box_title_hr = HR(color=ColorPalette.PRIMARY)
        self.add(box_title_hr)

        # ---- Zone "Description" ----
        left_box = toga.Box(style=Pack(flex=7, direction=COLUMN, margin=10, gap=5))
        description_label = LabelH3("Description")
        left_box.add(description_label)
        description_text = toga.MultilineTextInput(readonly=True, style=Pack(margin=10))
        description_text.value = current_issue['description']  # Texte long pour test du scroll
        left_box.add(toga.ScrollContainer(content=description_text, style=Pack(flex=1, height=300)))  # Scrollable

        # ---- Informations " ----
        left_box.add(LabelH3("Journal", margin_top=50))
        self.journal_note = toga.TextInput()
        left_box.add(self.journal_note)  # Scrollable
        left_box.add(LabelH3("Commentaires"))
        self.commentaire = toga.MultilineTextInput(style=Pack(margin=10, flex=1))
        left_box.add(toga.ScrollContainer(content=self.commentaire))  # Scrollable

        # ---- Zone "Lignes de texte" ----
        right_box = toga.Box(style=Pack(direction=COLUMN, flex=3, margin=10, gap=10))
        lines_label = LabelH3("Journal")
        lines_box = toga.Box(style=Pack(direction=COLUMN, gap=5))  # Ajout d'un margin pour séparation

        journals = current_issue['journals']
        for itm in journals:
            lines_box.add(toga.Label(itm))
        right_box.add(lines_label)
        right_box.add(toga.ScrollContainer(content=lines_box, style=Pack()))

        box_kpis = toga.Box(style=Pack(direction=COLUMN, gap=5, justify_content=CENTER, flex=1))
        # date action
        # Création du champ de date
        self.issue_date = widget_date.DateWidget()
        box_date = toga.Box(style=Pack(direction=COLUMN, flex=0.5),
                            children=[LabelH3("Date action"), self.issue_date])

        self.issue_time_tracked = toga.NumberInput(min=0, step=0.1, style=Pack(width=200))
        box_timer = toga.Box(style=Pack(direction=COLUMN, flex=0.5),
                             children=[LabelH3("Temps passé"), self.issue_time_tracked])

        box_kpis.add(toga.Box(style=Pack(gap=10, direction=ROW),
                              children=[box_date, box_timer])
                     )  # Scrollable

        box_kpis.add(toga.Box(style=Pack(gap=10, direction=ROW),
                              children=[LabelH3("Statut", flex=0.5), LabelH3("Activité", flex=0.5)])
                     )  # Scrollable

        self.issue_activities = toga.Selection(style=Pack(flex=0.5, margin=5),
                                               items=list(map(lambda dl: f'{dl[0]} - {dl[1]}',
                                                              project['time_entry_activities'])))
        self.issue_status = toga.Selection(items=list(map(lambda dl: f'{dl[0]} - {dl[1]}', redmine_status)),
                                           style=Pack(flex=0.5, margin=5))

        box_kpis.add(toga.Box(style=Pack(gap=5, direction=ROW),
                              children=[self.issue_status, self.issue_activities]))  # Scrollable

        # Bouton de connexion
        bottom_bar = toga.Box(
            style=Pack(direction=ROW, margin=5, justify_content="center", align_items="center", flex=1))

        button_validation = toga.Button("Validation", on_press=self.validation,
                                        style=Pack(justify_content=CENTER, width=200, margin=25))
        button_Cancel = toga.Button("Annuler", on_press=self.previous_screen,
                                    style=Pack(justify_content=CENTER, width=200, margin=25))
        bottom_bar.add(button_Cancel)
        bottom_bar.add(button_validation)
        box_kpis.add(HR(color=ColorPalette.SECONDARY))
        box_kpis.add(bottom_bar)
        right_box.add(HR(color=ColorPalette.SECONDARY))
        right_box.add(box_kpis)
        # ---- Conteneur principal (SplitContainer) ----
        infos_box = toga.Box(style=Pack(direction=ROW, margin=5), children=[left_box, right_box])
        self.add(infos_box)

    def previous_screen(self, *args, **kwargs):
        self.main_window.nextscreen('dashboard')

    def validation(self, *args, **kwargs):
        try:
            redmine_time = float(self.issue_time_tracked.value.strip())

            if redmine_time <= 0.0 or not self.issue_date.is_valid:
                raise ValueError()

            redmine_note = self.journal_note.value.strip()
            redmine_commentaire = self.commentaire.value.strip()
            redmine_activity = self.redmine_activity.selected_value.strip()

            for v in [redmine_note, redmine_commentaire, redmine_activity, redmine_time]:
                if not v:
                    raise ValueError()

            spent_on = self.issue_date.value

            redmine_status = self.redmine_status.selected_value
            redmine_status_id, redmine_status = spilt_uuid(redmine_status)
            redmine_activity_id, redmine_activity = spilt_uuid(redmine_activity)
            _, priority = spilt_uuid(self.priority)

            Constantine.nextcloud_account.post_activity(self.project, self.issue, self.description,
                                                        f'*{redmine_commentaire}*\n{redmine_note}',
                                                        redmine_status, self.category, priority, self.due_date)

            Constantine.redmine_account.post_activity(self.issue_id, redmine_time, spent_on, redmine_activity_id,
                                                      redmine_commentaire,
                                                      redmine_status_id, redmine_note, done_ratio=10)

        except Exception as ex:
            message = str(ex)
            dialog_box = toga.ErrorDialog("Connexion Redmine", message)
            asyncio.create_task(self.main_window.dialog(dialog_box))
