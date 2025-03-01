from redminelib.exceptions import AuthError

from redcloud_app.controllers import Constantine, Redminer
from redcloud_app.controllers.nexclouder import Nextclouder
from redcloud_app.views.templates import CWButtonOK, Background


class LoginButton(CWButtonOK):
    def on_press(self):
        self.get_parent().validation()



class  LoginScreen(Background):
    name = 'login'

    def validation(self):
        validation = False
        redmine_user = self.ids.redmine_user.text  # Récupère la valeur du champ de texte
        redmine_user_password = self.ids.redmine_password.text  # Récupère la valeur du champ de texte


        print(f"Enregistrement utilisateur ")  # Affiche le texte dans la console
        message = ""
        for item_str in [redmine_user, redmine_user_password]:
            if not item_str:
                self.show_message_popup(message, "Remplir le formulaire")
                return False
        try:
            Constantine.redmine_account, nextcloud_account = Redminer.login(
                redmine_user,
                redmine_user_password
            )
            Constantine.nextcloud_account = Nextclouder.login(redmine_user, redmine_user_password, **nextcloud_account) if nextcloud_account else None
            validation = True
        except FileExistsError as fex:
            message = fex.__str__()
        except AuthError as aex:
            message = aex.__str__()
        except Exception as ex:
            message = ex.__str__()
        finally:
            if validation:
                self.manager.current = 'otp_login'
            else:
                self.show_message_popup(message, "Erreur d'enregistrement")
