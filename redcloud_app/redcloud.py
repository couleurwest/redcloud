import toga
from dreamtools.logmng import CTracker
from toga.constants import COLUMN
from toga.style import Pack

from redcloud_app.controllers.authentication import Authentication
from redcloud_app.views.view_otp import OTPLoginScreen, OTPSigninScreen
from redcloud_app.views.view_dashboard import DashScreen
from redcloud_app.views.view_login import LoginScreen
from redcloud_app.views.view_nextcloud import NextcloudScreen
from redcloud_app.views.view_signin import SigninScreen


class RedcloudWindows(toga.MainWindow):
    pic: str = ''

    __main_box = None

    @property
    def main_box(self):
        if self.__main_box is None:
            header_image_style = Pack(margin=10)
            self.my_image = toga.Image("resources/redcloud.png")

            header_image = toga.ImageView(self.my_image, style=header_image_style)
            self.__main_box = toga.Box(children=[header_image], style=Pack(flex=1, direction=COLUMN))

        return self.__main_box

    def __init__(self, **kwargs):
        # Créer l'image en haut et le champ de texte
        super().__init__(title="Redcloud",**kwargs)
        CTracker.config('PRODUCTION')
        self.pic = toga.Image("resources/icon.png")
        self.screens = {
            'login_view': LoginScreen,
            'signin_view': SigninScreen,
            'nextcloud_view': NextcloudScreen,
            'otplogin_view': OTPLoginScreen,
            'otpsignin_view': OTPSigninScreen,
            'dashboard': DashScreen
        }

        content = 'login_view' if Authentication.check_config_file() else 'signin_view'
        self.nextscreen(content)

    def nextscreen(self, screename):
        self.content = self.screens[screename](self)
        # self.main_window.show()


class RedcloudApp(toga.App):
    def startup(self):
        self.main_window = RedcloudWindows(size=(640, 480))
        self.main_window.show()


def main():
    return RedcloudApp("Redcloud", "net.3p0.redcloud_app", icon="resources/icon.png", author="COULEUR WEST IT", description="Redcloud application")
