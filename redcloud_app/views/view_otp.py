import asyncio
import tempfile

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, CENTER, ROW
from toga.validators import MinLength, MaxLength

from redcloud_app.controllers import Constantine
from redcloud_app.controllers.authentication import Authentication
from redcloud_app.controllers.autorisation import show_qr_code, verify_otp, get_otp_code, generate_otp_secret
from redcloud_app.views.color_palette import ColorPalette
from redcloud_app.views.view_templates import BoxView, LabelH2, HR


class OTPLoginScreen(BoxView):
    name = 'otp_login'
    main_window = None


    def __init__(self, *args, **kwargs):

        # Champ utilisateur
        box_title = LabelH2('Code de vérification (OTP)')
        box_title_hr = HR(color=ColorPalette.SECONDARY)


        # Bouton de connexion
        bottom_bar = toga.Box(style=Pack(direction=COLUMN, margin=5, justify_content="center", align_items="center", flex=1))
        self.otp_input = toga.TextInput(style=Pack(text_align=CENTER, margin=10, font_size=20, height=50, width=150), validators = [ MinLength(6), MaxLength(6)] )
        button_validation = toga.Button("Validation", on_press=self.validation, style=Pack(justify_content=CENTER, width=200, margin=25))
        bottom_bar.add(self.otp_input)
        bottom_bar.add(button_validation)

        super().__init__(style=Pack(direction=COLUMN, margin=10, gap=10, justify_content=CENTER),
                         children=[box_title, box_title_hr,bottom_bar])

    def validation(self, instance, **kwargs):
        if self.otp_input.value and self.otp_input.is_valid :
            """Vérifie le code OTP saisi."""
            otp_secret= Constantine.redmine_account.otp_secret
            otp_code = self.otp_input.value.strip()
            otp_code = get_otp_code (otp_secret)

            if verify_otp(otp_secret, otp_code):
                current = 'dashboard'
                self.main_window.nextscreen(current)
                self.delete_me()
            else:
                info_dialog = toga.InfoDialog("Code incorrect. Réessayez.", "Code OTP")
                task = asyncio.create_task(self.main_window.dialog(info_dialog))

class OTPSigninScreen(BoxView):
    name = 'otp_signin'
    main_window = None


    otp_secret:str
    user_email:str


    def __init__(self, *args, **kwargs):
        # Créer le contenu gauche (panel de navigation)
        # Load an image for the background
        self.secret_key = generate_otp_secret()
        self.user_email = Constantine.redmine_account.redmine_login

        buffer = show_qr_code(self.secret_key, self.user_email)

        # Sauvegarder l'image temporairement
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            temp_file.write(buffer.getvalue())  # Extraire les bytes depuis BytesIO
            temp_file_path = temp_file.name  # Récupérer le chemin du fichier temporaire

        # Charger l'image depuis le fichier
        qrotp_image = toga.Image(temp_file_path)

        image_view = toga.ImageView(qrotp_image, style=Pack(margin=10, height=300))
        sk_label = toga.Label("Secret key:", style=Pack(margin=5))
        self.secret_key_input = toga.TextInput()
        self.secret_key_input.value = self.secret_key

        left_box = toga.Box(style=Pack( margin=10, direction=COLUMN, gap=20), children=[image_view, sk_label, self.secret_key_input])

        box_title = LabelH2('Verification')
        box_title_hr = HR(color='firebrick')

        codeotp_label = toga.Label("Entrez le code OTP:", style=Pack(margin=5))
        self.otp_input = toga.TextInput( )
    
        button_validation = toga.Button("Vérifier", on_press=self.validation)
        # Créer le contenu droit
        right_box = toga.Box(style=Pack( margin=20, direction=COLUMN, gap=20, align_items=CENTER, justify_content="start"),
                               children=[box_title, box_title_hr, codeotp_label, self.otp_input, button_validation])
        # ---- Conteneur principal (SplitContainer
        infos_box = toga.box(toga.Box(style=Pack(direction=ROW, gap=20),
                               children=[left_box, right_box]))

        super().__init__(children=[infos_box], style=Pack(flex=1))
       
       
    def validation(self, *args, **kwargs):
        """Vérifie le code OTP saisi."""

        otp_code = self.otp_input.value.strip()
        otp_code = get_otp_code (self.secret_key)

        if verify_otp(self.secret_key, otp_code):
            data = Constantine.redmine_account.document()
            data['otp_secret'] = self.secret_key
            data.update(**Constantine.nextcloud_account.document())
            Authentication.encrypt_data(data, Constantine.redmine_account.redmine_password)

            print("✅ Fichier sécurisé créé avec succès.")

            self.main_window.nextscreen('dashboard')
            self.delete_me()
        else:
            info_dialog = toga.InfoDialog("Code incorrect. Réessayez.", "Code OTP")
            task = asyncio.create_task(self.main_window.dialog(info_dialog))
