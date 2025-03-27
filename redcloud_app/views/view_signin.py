import asyncio

import toga
from redminelib.exceptions import AuthError

from toga.style import Pack
from toga.style.pack import COLUMN, CENTER

from redcloud_app.controllers import Constantine, Redminer
from redcloud_app.views.color_palette import ColorPalette
from redcloud_app.views.view_templates import LabelH1, HR, BoxView


class SigninScreen(BoxView):
    name = 'signin'
    main_window = None


    def __init__(self, *args, **kwargs):
        # Champ utilisateur
        box_title = LabelH1('Redcloud')
        box_title_hr = HR(color=ColorPalette.PRIMARY)

        username_label = toga.Label("Login:", style=Pack(margin=5))
        self.username_input = toga.TextInput(placeholder="Entrez votre login redmine")
        self.username_input.value = "dreamgeeker"

        # Champ mot de passe
        password_label = toga.Label("Mot de passe:", style=Pack(margin=5))
        self.password_input = toga.PasswordInput()
        self.password_input.value = 'Dr3@mK!tch5R#76'

        box_subtitle_hr = HR(color=ColorPalette.SECONDARY)


        url_label = toga.Label("URL:", style=Pack(margin=5))
        self.url_redmine = toga.TextInput(placeholder="https://cie.redminer.me", style=Pack(margin=5))
        self.url_redmine.value = "https://workflow.couleurwest-it.com"

        apikey_label = toga.Label("Clé API", style=Pack(margin=5))
        self.api_key = toga.PasswordInput()
        self.api_key.value = "815f1976f3b9536c839bd04f1bf875aa0aec6926"

        # Bouton de connexion


        # Bouton de connexion
        bottom_bar = toga.Box(style=Pack(direction=COLUMN, margin=5, justify_content="center", align_items="center", flex=1))
        button_validation = toga.Button("Validation", on_press=self.validation, style=Pack(justify_content="end", width=200))
        bottom_bar.add(button_validation)

        super().__init__(style=Pack(direction=COLUMN, align_items=CENTER, margin=10, gap=10),
                         children=[box_title, box_title_hr, username_label, self.username_input, password_label,
                                   self.password_input,url_label, self.url_redmine,
                                   apikey_label, self.api_key,  box_subtitle_hr, bottom_bar])

    def validation(self, *args, **kwargs):
        redmine_user = self.username_input.value.strip()
        redmine_user_password = self.password_input.value.strip()
        redmine_url = self.url_redmine.value.strip()
        redmine_key = self.api_key.value.strip()
        dialog_box = None

        try:
            for v in (redmine_user, redmine_user_password,redmine_url,redmine_key):
                if not v:
                    raise Warning("Formulaire à compléter")

            Constantine.redmine_account = Redminer.signin(
                redmine_user, redmine_user_password,
                redmine_key, redmine_url
            )

            self.main_window.nextscreen('nextcloud_view')
            self.delete_me()

            dialog_box = toga.InfoDialog("Connexion Redmine", "Connexion réussie")
        except AuthError as e:
            dialog_box = toga.ErrorDialog("Connexion Redmine", "Erreur d'identification")
        except Exception as e:
            message = str(e)
            dialog_box = toga.ErrorDialog("Connexion Redmine", message)
        finally:
            asyncio.create_task(self.main_window.dialog(dialog_box))
