from kivy.core.image import Image as CoreImage
from kivy.uix.screenmanager import Screen

from redcloud_app.controllers import Constantine
from redcloud_app.controllers.autorisation import show_qr_code, verify_otp, get_otp_code
from redcloud_app.views.templates import Background, CWButtonOK


class OTPButton(CWButtonOK):
    def on_press(self):
        self.get_parent().validation()

class OTPScreen(Background):

    def validation(self):
        """Vérifie le code OTP saisi."""
        otp_secret= Constantine.redmine_account.otp_secret

        otp_code = self.ids.otp_input.text.strip()
        if verify_otp(otp_secret, otp_code):
            self.manager.current = 'main'
        else:
            self.show_message_popup("Code incorrect. Réessayez.", "Code OTP")


class OTPLoginScreen(OTPScreen):
    name = 'otp_login'

#        buffer.seek(0)
    def validation(self):
        """Vérifie le code OTP saisi."""
        otp_secret= Constantine.redmine_account.otp_secret
        otp_code = self.ids.otp_input.text.strip()
        otp_code = get_otp_code (otp_secret)
        if verify_otp(otp_secret, otp_code):
            self.manager.current = 'dashboard' if Constantine.nextcloud_account else 'nextcloud'
        else:
            self.show_message_popup("Code incorrect. Réessayez.", "Code OTP")

class OTPSigninScreen(OTPScreen):
    name = 'otp_signin'

    otp_secret:str
    user_email:str

    def on_pre_enter(self):
        """Génère et affiche le QR Code à chaque affichage du screen."""
        self.show_qr_code()

    def show_qr_code(self):
        """Génère le QR Code basé sur la clé OTP et l'affiche dans l'Image widget."""
        otp_secret, user_email = Constantine.redmine_account.get_otp_param()
        buffer = show_qr_code(otp_secret, user_email)

        self.ids.qrcode_image.texture = CoreImage(buffer, ext="png").texture
        self.ids.secret_key.text = f"Clé secrète : {otp_secret}"
