import asyncio
import re

import toga
from dreamtools.logmng import CTracker
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER

from redcloud_app.controllers import Constantine
from redcloud_app.controllers.toolbox import spilt_uuid
from redcloud_app.views import widget_date
from redcloud_app.views.color_palette import ColorPalette
from redcloud_app.views.view_templates import LabelH2, HR, BoxView, LabelH3

def validate_input(value):
    """ Vérifie si l'entrée est un nombre décimal > 0 """
    value = value.strip()
    if re.fullmatch(r"\d+(\.\d+)?", value):  # Vérifie si c'est un nombre
        if float(value) > 0:  # Vérifie si > 0
            return None
        return "Entrez un nombre décimal valide > 0"

class BoardScreen(BoxView):
    issue_id: int = 0
    project_name = ''
    issue_title = ''
    issue_category = ''
    due_date = None
    description = ''
    priority = ''

    def __init__(self, *args, **kwargs):
        super().__init__(style=Pack(direction=COLUMN, flex=1, margin=5, gap=5), *args, **kwargs)
        self.issue_priority = None
        self.issue_description = None
        self.label_projet = LabelH2("Projet", color=ColorPalette.PRIMARY, flex=0.3)

        self.label_subject = LabelH2("subject", color=ColorPalette.ACCENT, flex=0.3)
        self.label_category = LabelH2("category", color=ColorPalette.SECONDARY, flex=0.2)
        self.label_tracker = LabelH3("tracker", color=ColorPalette.SECONDARY, flex=0.2)
        self.label_priority = LabelH3("priority", color=ColorPalette.SECONDARY, flex=0.2)
        self.label_status = LabelH3("status", color=ColorPalette.SECONDARY, flex=0.1)

        #entete de présentation
        header = toga.Box(style=Pack(direction=ROW, gap=5))
        header.add(self.label_projet)
        header.add(LabelH2("Catégorie", flex=0.2, color=ColorPalette.ACCENT))
        header.add(LabelH2("Tracker", flex=0.2, color=ColorPalette.ACCENT))
        header.add(LabelH2("Priorité", flex=0.2, color=ColorPalette.ACCENT))
        header.add(LabelH2("Statut", flex=0.1, color=ColorPalette.ACCENT))
        self.add(header)

        header = toga.Box(style=Pack(direction=ROW, gap=5))
        header.add(self.label_subject)
        header.add(self.label_category)
        header.add(self.label_tracker)
        header.add(self.label_priority)
        header.add(self.label_status)
        self.add(header)

        self.add(HR(color=ColorPalette.PRIMARY))

    # ---- Zone "Description" ----
        self.journal_note = toga.TextInput()

        self.label_description = toga.MultilineTextInput(readonly=True, style=Pack(margin=10))
        widget = toga.ScrollContainer(content= self.label_description, style=Pack(flex=1, height=300))  # Scrollable
        self.commentaire = toga.MultilineTextInput( style=Pack(margin=10))
        widget2 = toga.ScrollContainer(content= self.commentaire, style=Pack(flex=1, height=300))  # Scrollable

        left_box = toga.Box(style=Pack(flex=7, direction=COLUMN, margin=10, gap=5),
                            children=[
                                LabelH3("Description"),
                                widget, LabelH3("Journal", margin_top=50),
                                self.journal_note,
                                LabelH3("Commentaire"),widget2])

        self.label_journal = toga.Box(style=Pack(direction=COLUMN, gap=5))  # Ajout d'un margin pour séparation
        #----------------------------------------------------------------------------------
        box_kpis = toga.Box(style=Pack(direction=COLUMN, gap=5, justify_content=CENTER, flex=1), margin_top=50)
        # date action
        # Création du champ de date
        self.issue_date = widget_date.DateWidget()
        box_date = toga.Box(style=Pack(direction=COLUMN, flex=0.5),
                            children=[LabelH3("Date action"), self.issue_date])

        self.issue_time_tracked = toga.TextInput(value=1.0, style=Pack(width=200), validators=[validate_input])
        box_timer = toga.Box(style=Pack(direction=COLUMN, flex=0.5),
                             children=[LabelH3("Temps passé"), self.issue_time_tracked])

        box_kpis.add(toga.Box(style=Pack(gap=10, direction=ROW), children=[box_date, box_timer]))  # Scrollable

        box_kpis.add(toga.Box(style=Pack(gap=10, direction=ROW),
                              children=[LabelH3("Statut", flex=0.5), LabelH3("Activité", flex=0.5)])
                     )  # Scrollable

        self.issue_activities = toga.Selection(style=Pack(flex=0.5, margin=5), items=[])
        self.issue_status = toga.Selection(items=[], style=Pack(flex=0.5, margin=5))

        box_kpis.add(toga.Box(style=Pack(gap=5, direction=ROW),
                              children=[self.issue_status, self.issue_activities]))  # Scrollable


        # Bouton de connexion
        bottom_bar = toga.Box(
            style=Pack(direction=ROW, margin=5, justify_content="center", align_items="center", flex=1))

        button_validation = toga.Button("Validation", on_press=lambda it: asyncio.create_task(self.validation()),
                                        style=Pack(justify_content=CENTER, width=200, margin=25))
        button_cancel = toga.Button("Annuler", on_press=self.previous_screen,
                                    style=Pack(justify_content=CENTER, width=200, margin=25))

        bottom_bar.add(button_cancel)
        bottom_bar.add(button_validation)

        right_box = toga.Box(style=Pack(direction=COLUMN, flex=3, margin=10, gap=10), children=[
            LabelH3("Journal"),
            toga.ScrollContainer(content=self.label_journal, style=Pack()),
            HR(color=ColorPalette.SECONDARY),
            box_kpis,
            HR(color=ColorPalette.SECONDARY),bottom_bar

        ])

        # ---- Conteneur principal (SplitContainer) ----
        infos_box = toga.Box(style=Pack(direction=ROW, margin=5), children=[left_box, right_box])
        self.add(infos_box)

    def populate_screen(self, issue_id):
        self.issue_id = int(issue_id)

        # while self.children:
        #     self.remove(self.children[0])

        # Récupération des données relatives au projet en cours (issue_id)
        redmine_account = Constantine.redmine_account
        redmine_issues = redmine_account.issues
        redmine_status = redmine_account.status

        current_issue = redmine_issues[self.issue_id]

        project = redmine_account.projects[current_issue['project_id']]
        self.project_name =  project["name"]
        self.label_projet.text = f"#{issue_id}-" + self.project_name
        CTracker.info_tracking('Gestion projet', 'Dashboard')
        self.issue_title = current_issue['subject']
        self.issue_category = self.label_category.text = current_issue.get('category', '')
        self.due_date = current_issue.get('due_date', '')
        self.issue_description = current_issue.get('description', '')
        self.issue_priority = current_issue.get('priority', '')

        #Mise à jour de l'ecran
        self.label_subject.text = current_issue['subject']
        self.label_tracker.text = current_issue.get('tracker', '')
        self.label_priority.text =  self.issue_priority + f' [{self.due_date }]'
        self.label_status = current_issue['status']

        self.issue_time_tracked.value = 1.0
        self.issue_date.reset_date()
        self.commentaire.value = ''
        self.journal_note.value = ''
        # ---- Information ----
        self.label_description.value = self.issue_description  # Texte long pour test du scroll

        # ---- Zone "Lignes de texte" ----


        journals = current_issue['journals']
        self.label_journal.clear()

        for itm in journals:
            self.label_journal.add(toga.Label(itm))

        self.issue_status.items = list(map(lambda dl: f'{dl[0]} - {dl[1]}', redmine_status))
        self.issue_activities.items = list(map(lambda dl: f'{dl[0]} - {dl[1]}', project['time_entry_activities']))

    def previous_screen(self, *args, **kwargs):
        self.main_window.nextscreen('dashboard')

    async def validation(self, *args, **kwargs):
        try:
            CTracker.info_tracking('Update projet', 'Dashboard')
            if not  self.issue_time_tracked.is_valid or not self.issue_date.is_valid:
                raise ValueError()

            redmine_time = float(self.issue_time_tracked.value)
            redmine_note = self.journal_note.value.strip()
            redmine_commentaire = self.commentaire.value.strip()

            for v in [redmine_note, redmine_commentaire, redmine_time]:
                if not v:
                    raise ValueError()

            redmine_activity = self.issue_activities.value.strip()
            redmine_status = self.issue_status.value.strip()

            spent_on = self.issue_date.value

            redmine_status_id, redmine_status = spilt_uuid(redmine_status)
            redmine_activity_id, redmine_activity = spilt_uuid(redmine_activity)
            _, priority = spilt_uuid(self.priority)

            CTracker.info_tracking('Update projet Nextcloud', 'Dashboard')

            await Constantine.nextcloud_account.post_activity(self.project_name, self.issue_title, self.issue_description,
                                                        f'*{redmine_commentaire}*\n{redmine_note}',
                                                        redmine_status, self.issue_category, self.priority, self.due_date)

            CTracker.info_tracking('Update projet Redmine', 'Dashboard')
            Constantine.redmine_account.post_activity(self.issue_id, redmine_time, spent_on, redmine_activity_id,
                                                      redmine_commentaire,
                                                      redmine_status_id, redmine_note, done_ratio=10)

        except Exception as ex:
            message = ex.__str__()
            CTracker.error_tracking(message, "viewboard")
            dialog_box = toga.ErrorDialog("Connexion Redmine", message)
            asyncio.create_task(self.main_window.dialog(dialog_box))
