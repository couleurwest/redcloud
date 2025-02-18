from redminelib.exceptions import AuthError
from scripts.regsetup import FileExists

from redcloud_app.controllers import Constantine
from redcloud_app.controllers.redminer import Redminer
from redcloud_app.views.templates import CWButtonOK, Background


class SigninButton(CWButtonOK):
    pass


class SigninScreen(Background):
    name = 'signin'

    def validation(self):
        validation = False
        redmine_user = self.ids.redmine_user.text  # Récupère la valeur du champ de texte
        redmine_user_password = self.ids.redmine_password.text  # Récupère la valeur du champ de texte
        redmine_url = self.ids.redmine_url.text  # Récupère la valeur du champ de texte
        redmine_key = self.ids.redmine_key.text  # Récupère la valeur du champ de texte

        print(f"Enregistrement utilisateur ")  # Affiche le texte dans la console
        message = ""
        for item_str in [redmine_user, redmine_user_password,redmine_url,redmine_key]:
            if not item_str:
                self.show_message_popup(message, "Remplir le formulaire")
                return False
        try:
            Constantine.redmine_account = Redminer.signin(
                redmine_user,
                redmine_user_password,
                redmine_key,
                redmine_url
            )
            Constantine.nextcloud_account = None
            validation = True
        except FileExistsError as fex:
            message = fex.__str__()
        except AuthError as aex:
            message = aex.__str__()
        except Exception as ex:
            message = ex.__str__()
        finally:
            if validation:
                self.manager.current = 'otp_signin'
            else:
                self.show_message_popup(message, "Erreur d'enregistrement")
