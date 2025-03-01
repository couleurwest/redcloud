from redminelib.exceptions import AuthError

from redcloud_app.controllers import Constantine, Nextclouder
from redcloud_app.views.templates import CWButtonOK, Background


class LoginNextcloudButton (CWButtonOK):
    pass

class NextcloudScreen(Background):
    name = 'nextcloud'

    nextcloud_user: str
    nextcloud_password: str
    nextcloud_url: str

    def validation(self):
        validation = False
        nextcloud_user = self.ids.nextcloud_user.text  # Récupère la valeur du champ de texte
        nextcloud_password = self.ids.nextcloud_password.text  # Récupère la valeur du champ de texte
        nextcloud_url = self.ids.nextcloud_url.text  # Récupère la valeur du champ de texte

        print(f"Connexion utilisateur ")  # Affiche le texte dans la console
        message = ""

        for item_str in [nextcloud_user, nextcloud_password,nextcloud_url]:
            if not item_str:
                self.show_message_popup(message, "Remplir le formulaire")
                return False
        try:
            Constantine.nextcloud_account = Nextclouder.login(
                Constantine.redmine_account.redmine_login,
                Constantine.redmine_account.redmine_password,
                nextcloud_user,
                nextcloud_password,
                nextcloud_url
            )
            validation = True
        except FileExistsError as fex:
            message = fex.__str__()
        except AuthError as aex:
            message = aex.__str__()
        except Exception as ex:
            message = ex.__str__()
        finally:
            if validation:
                self.manager.current = 'dashboard'
            else:
                self.show_message_popup(message, "Erreur - Conexion Nextcloud")
