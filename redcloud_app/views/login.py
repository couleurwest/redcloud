from redcloud_app.views.templates import CWButtonOK, CWButtonCancel


class LoginButton(CWButtonOK):
    def action(self):
        print("Bouton OK du LoginScreen pressé")



class CancelButton(CWButtonCancel):
    def action(self):
        print("Bouton Cancel du LoginScreen pressé")

