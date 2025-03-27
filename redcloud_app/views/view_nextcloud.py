import asyncio

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, CENTER

from redcloud_app.controllers import Constantine, Nextclouder
from redcloud_app.views.color_palette import ColorPalette
from redcloud_app.views.view_templates import BoxView, LabelH2, HR


class NextcloudScreen(BoxView):
    name = 'nextcloud'
    main_window = None


    def __init__(self, *args, **kwargs):
        # Champ utilisateur
        box_title = LabelH2('Nextcloud')
        box_title_hr = HR(color=ColorPalette.PRIMARY)

        username_label = toga.Label("Login:", style=Pack(margin=5))
        self.nextcloud_user = toga.TextInput(placeholder="Entrez votre pseudo")
        self.nextcloud_user.value = "dreamgeeker"

        # Champ mot de passe
        password_label = toga.Label("Mot de passe:", style=Pack(margin=5))
        self.nextcloud_password = toga.PasswordInput()

        box_subtitle_hr = HR(color=ColorPalette.SECONDARY)

        url_label = toga.Label("URL:", style=Pack(margin=5))
        self.nextcloud_url = toga.TextInput(placeholder="https://cie.redminer.me", style=Pack(margin=5))

        # Bouton de connexion
        button_validation = toga.Button("Enregistrement", on_press=lambda widget: asyncio.create_task(self.validation()))
        super().__init__(style=Pack(direction=COLUMN, align_items=CENTER, margin=10, gap=10),
                         children=[box_title, box_title_hr, username_label, self.nextcloud_user, password_label,
                                   self.nextcloud_password, url_label, self.nextcloud_url, box_subtitle_hr, button_validation])

    async def validation(self, *args, **kwargs):
        dialog_box = None
        nextcloud_user = self.nextcloud_user.value.strip()
        nextcloud_password = self.nextcloud_password.value.strip()
        nextcloud_url = self.nextcloud_url.value.strip()

        try:
            for item_str in (nextcloud_user, nextcloud_password,nextcloud_url):
                if not item_str:
                    raise Warning("Nom d'utilisateur ou mot de passe incorrect.")

            Constantine.nextcloud_account = await Nextclouder.login(nextcloud_user,nextcloud_password,nextcloud_url)

            if Constantine.redmine_account.otp_secret:
                self.main_window.nextscreen('otplogin_view')
            else:
                self.main_window.nextscreen('otpsignin_view')

            self.delete_me()
            dialog_box = toga.InfoDialog("Connexion Nextcloud", "Connexion réussie !")
        except Exception as ex:
            message = ex.__str__()
            print(message)
            # dialog_box = toga.ErrorDialog("Connexion Nextcloud", message)
        finally:
            pass
            # asyncio.create_task(self.main_window.dialog(dialog_box))
