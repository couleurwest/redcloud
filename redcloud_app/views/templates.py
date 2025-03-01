# templates.py
"""Gabarit thématique pour les éléments d'interface Kivy.

Ce module définit des composants préformatés et préconfigurés pour assurer une cohérence visuelle et fonctionnelle
au sein de l'application, incluant des arrière-plans, des labels, des champs de texte et des boutons avec des thèmes.
"""
from kivy.app import App
from kivy.core.window import Window
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.spinner import SpinnerOption, Spinner
from kivy.uix.textinput import TextInput

from redcloud_app.views.theme import ThemeNormal, ThemeDark

class MessageBox(BoxLayout):
    pass
class Background(Screen):
    """Arrière-plan de l'application avec gestion du thème.

    Attributes:
        theme (ThemeNormal or ThemeDark): Thème actuel de l'application.
    """
    name=None
    pages = []

    _theme = ThemeNormal()

    def __init__(self, **kwargs):
        super(Background, self).__init__(**kwargs)
        if self.name and self.name not in Background.pages:
            Background.pages.append(self.name)
        print (f"enter in {self.name} /  + {Background.pages}")

    def show_message_popup(self, message, erreur="Erreur"):
        """ Affiche un popup d'erreur avec un message personnalisé. """
        layout = MessageBox()
        layout.ids.message.text=message
        close_button = layout.ids.button_dismiss
        popup = Popup(title=erreur, content=layout, size_hint=(None, None), size=(300, 200), auto_dismiss=True)

        close_button.bind(on_press=popup.dismiss)  # Ferme la popup lorsqu'on appuie sur OK

        popup.open()

    @property
    def theme(self):
        return Background._theme

    @staticmethod
    def switch_theme(dark_mode):
        """Change le thème entre clair et sombre.

        Args:
            dark_mode (bool): True pour activer le mode sombre, False pour le mode clair.

        Returns:
            ThemeNormal or ThemeDark: Le thème sélectionné.
        """
        Background._theme = ThemeDark() if dark_mode else ThemeNormal()
        return Background._theme

    def _set_screen(self):
        self.manager.current = Background.pages[self.indice]

    def set_screen(self, pages_name):
        self.indice = Background.pages.index(pages_name)
        self._set_screen()

    @property
    def next_screen(self):
        self.indice += 1
        if self.indice == len(Background.pages):
            self.indice = 0

        self._set_screen()


# Éléments de texte
class CWSpinnerOption(SpinnerOption):
    """Label de base utilisé pour afficher du texte."""
    is_hovered = BooleanProperty(False)  # Survol
    is_pressed = BooleanProperty(False)  # Clic

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_move)

    def on_press(self):
        self.is_pressed= True

    def on_release(self):
        self.is_pressed=False

    def on_mouse_move(self, window, pos):
        """Détecte si la souris survole le bouton.

        Args:
            window (Window): Fenêtre actuelle.
            pos (tuple): Position actuelle de la souris (x, y).
        """

        self.is_hovered = self.collide_point(*self.to_widget(*pos))

class CWSpinner(Spinner):
    is_hovered = BooleanProperty(False)  # Survol
    is_pressed = BooleanProperty(False)  # Clic
    selected_value = StringProperty("")  # Clic
    text_init = True
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_move)
        self.bind(text=self.set_selection)

    @property
    def theme(self):
        return Background.theme

    def set_selection(self, spinner, text):
        if self.text_init:
            self.text_init = False
        else:
            self.selected_value = text

    def on_press(self):
        self.is_pressed = True

    def on_release(self):
        self.is_pressed = False

    def on_mouse_move(self, window, pos):
        """Détecte si la souris survole le bouton.

        Args:
            window (Window): Fenêtre actuelle.
            pos (tuple): Position actuelle de la souris (x, y).
        """

        self.is_hovered = self.collide_point(*self.to_widget(*pos))

# Éléments de texte
class CWSimpleText(Label):
    """Label de base utilisé pour afficher du texte."""
    pass

class CWLink(Button):
    is_hovered = BooleanProperty(False)  # Survol
    was_hovered = BooleanProperty(False)  # Survol
    is_pressed = BooleanProperty(False)  # Clic
    text_base = ""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_move)
    def on_press(self):
        self.is_pressed = True

    def on_release(self):
        self.is_pressed = False

    def on_mouse_move(self, window, pos):
        """Détecte si la souris survole le bouton.

        Args:
            window (Window): Fenêtre actuelle.
            pos (tuple): Position actuelle de la souris (x, y).
        """

        self.is_hovered = self.collide_point(*self.to_widget(*pos))

        if self.is_hovered != self.was_hovered:
            if not self.text_base:
                self.text_base = self.text
            self.text = f"[u]{self.text_base}[/u]" if self.is_hovered else self.text_base

            window.set_system_cursor("hand" if self.is_hovered else "arrow")
            self.was_hovered = self.is_hovered



class Title1(CWSimpleText):
    """Titre de niveau 1."""
    pass

class Title2(CWSimpleText):
    """Titre de niveau 2."""
    pass

class Title3(CWSimpleText):
    """Titre de niveau 3."""
    pass

# Formulaire
class CWTextInput(TextInput):
    """Champ de texte personnalisé avec détection de survol.

    Attributes:
        is_hovered (bool): Indique si la souris est au-dessus du champ.
    """

    is_hovered = BooleanProperty(False)  # Survol

    def __init__(self, **kwargs):
        """Initialise le champ de texte et lie la détection de la souris."""
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_move)

    def on_mouse_move(self, window, pos):
        """Détecte si la souris survole le champ de texte.

        Args:
            window (Window): Fenêtre actuelle.
            pos (tuple): Position actuelle de la souris (x, y).
        """
        self.is_hovered = self.collide_point(*pos)


# Boutons
class ButtonTheme(Button):
    """Bouton stylisé avec gestion du thème et de l'état (survol et pression).

    Attributes:
        theme (ThemeNormal or ThemeDark): Thème du bouton.
        is_hovered (bool): Indique si la souris survole le bouton.
        is_pressed (bool): Indique si le bouton est enfoncé.
    """

    theme = ThemeNormal()  # Thème par défaut
    is_hovered = BooleanProperty(False)  # Survol
    is_pressed = BooleanProperty(False)  # Clic

    def __init__(self, **kwargs):
        """Initialise le bouton avec détection de la souris."""
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_move)
    def on_press(self):
        self.is_pressed = True
    def on_release(self):
        self.is_pressed = False

    def on_mouse_move(self, window, pos):
        """Détecte si la souris survole le bouton.

        Args:
            window (Window): Fenêtre actuelle.
            pos (tuple): Position actuelle de la souris (x, y).
        """
        self.is_hovered = self.collide_point(*pos)


    def get_parent(self):
        parent = self.parent
        while parent and not isinstance(parent, Screen):
            parent = parent.parent
        return parent  # Retourne le Screen si trouvé, sinon None

class CWButton(ButtonTheme):
    pass

class CWButtonCancel(ButtonTheme):
    """Bouton d'annulation."""
    def on_press(self):
        App.get_running_app().stop()

class CWButtonOK(ButtonTheme):
    """Bouton de validation."""
    def on_press(self):
        self.get_parent().validation()


class DateInput(CWTextInput):
    def insert_text(self, substring, from_undo=False):
        """Ajoute une validation au format JJ/MM/AAAA"""
        if not substring.isdigit() and substring != "/":
            return  # Empêche l'entrée de lettres et autres symboles

        text = self.text + substring  # Prévisualise l'entrée
        if len(text) > 10:
            return  # Empêche d'écrire plus de 10 caractères

        # Ajoute automatiquement les '/' aux bonnes positions
        if len(text) in [2, 5] and substring != "/":
            substring += "/"

        super().insert_text(substring, from_undo=from_undo)