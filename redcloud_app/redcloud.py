from kivy.config import Config

from redcloud_app.controllers.toolbox import read_config

Config.set('kivy', 'window_title', 'Mon Application Kivy')

from kivy.app import App
from kivy.core.window import Window

from redcloud_app.views.templates import Background
from redcloud_app.views.theme import ThemeDark, ThemeNormal

from kivy.uix.screenmanager import SwapTransition, CardTransition, NoTransition, ShaderTransition
from kivy.uix.screenmanager import ScreenManager

class SigninScreen(Background):
    name = 'signin'

class  SigninNextcloudScreen(Background):
    name = 'nextcloud'

class  LoginScreen(Background):
    name = 'login'

class MainScreen(Background):
    name = "main"




# class Formulaire(BoxLayout):
#     pass
class RCScreenManager(ScreenManager):

    def on_current(self, instance, value):
        """ Change le titre de la fenêtre en fonction de l'écran actif """
        super().on_current(instance, value)

class RedcloudApp(App):
    theme = ThemeNormal()  # Thème par défaut
    config_path = "assets/.config.yaml"  # Modifier selon l'emplacement réel
    # __status = None

    def switch_theme(self, dark_mode):
        """Change le thème entre clair et sombre"""
        self.theme = ThemeDark() if dark_mode else ThemeNormal()

    def build(self):

        sm = RCScreenManager()
        sm.transition = NoTransition()

        sm.add_widget(MainScreen(name="main"))
        sm.current = "main"

        sm.add_widget(SigninScreen(name="signin"))
        sm.add_widget(SigninNextcloudScreen(name="nextcloud"))
        sm.add_widget(LoginScreen(name="login"))

        self.__status = read_config(self.config_path)
        current_screen = "login" if self.__status == "Complete" else self.__status if self.__status else "signin"
        print("current screen =", current_screen)
        sm.current = current_screen

        self.title = 'Redcloud 3.0'
        self.icon = "visuels/icon.png"

        return sm

# Paramètres de la fenêtre
Window.size = (600, 480)


if __name__ == "__main__":

    #FormsApp().run()
    RedcloudApp().run()
