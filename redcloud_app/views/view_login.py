import asyncio

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, CENTER, BOTTOM, ROW

from redcloud_app.controllers import Constantine, Redminer, Nextclouder
from redcloud_app.views.color_palette import ColorPalette
from redcloud_app.views.view_templates import LabelH1, HR, BoxView


class LoginScreen(BoxView):
    name = 'login'

    def __init__(self, *args, **kwargs):

        box_title = LabelH1('Redcloud')
        box_title_hr = HR(color=ColorPalette.PRIMARY)

        username_label = toga.Label("Login:", style=Pack(margin=5))
        self.username_input = toga.TextInput(placeholder="Login")
        self.username_input.value = "dreamgeeker"

        # Champ mot de passe
        password_label = toga.Label("Mot de passe:", style=Pack(margin=5))
        self.password_input = toga.PasswordInput(placeholder="Mot de passe")
        self.password_input.value = 'Dr3@mK!tch5R#76'

        box_subtitle_hr = HR(color=ColorPalette.SECONDARY)

        # Bouton de connexion
        bottom_bar = toga.Box(style=Pack(direction=COLUMN, margin=5, justify_content="center", align_items="center", flex=1))
        button_validation = toga.Button("Connexion", on_press=self.validation, style=Pack(justify_content="end", width=200))

        bottom_bar.add(button_validation)
        super().__init__(style= Pack(direction=COLUMN, align_items=CENTER, margin=10, gap=10),
                         children = [box_title, box_title_hr, username_label,self.username_input, password_label, self.password_input, box_subtitle_hr,  bottom_bar])

    def validation(self, *args, **kwargs):
        is_valid = False
        message = ""
        redmine_user = self.username_input.value.strip()
        redmine_user_password = self.password_input.value.strip()

        for v in (redmine_user, redmine_user_password):
            if not v:
                info_dialog = toga.ErrorDialog("Erreur", "Identifiants incorrects")
                asyncio.create_task(self.main_window.dialog(info_dialog))

                return False
        try:
            Constantine.redmine_account, nextcloud_account = Redminer.login(
                redmine_user,
                redmine_user_password
            )
            print ('suite')
            is_valid = True
        except Exception as ex:
            message = ex.__str__()
        finally:
            if is_valid:
                self.main_window.nextscreen('otplogin_view')
                self.delete_me()
            else:
                info_dialog = toga.InfoDialog("Erreur d'enregistrement", message)
                asyncio.create_task(self.main_window.dialog(info_dialog))