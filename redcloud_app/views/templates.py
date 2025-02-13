# templates.py
"""Gabarit thématique pour les éléments d'interface Kivy.

Ce module définit des composants préformatés et préconfigurés pour assurer une cohérence visuelle et fonctionnelle
au sein de l'application, incluant des arrière-plans, des labels, des champs de texte et des boutons avec des thèmes.
"""

from kivy.core.window import Window
from kivy.properties import BooleanProperty
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput

from redcloud_app.views.theme import ThemeNormal, ThemeDark


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
class CWLabel(Label):
    """Label de base utilisé pour afficher du texte."""


class Title1(CWLabel):
    """Titre de niveau 1."""


class Title2(CWLabel):
    """Titre de niveau 2."""


class Title3(CWLabel):
    """Titre de niveau 3."""


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

    def on_touch_down(self, touch):
        """Gère l'événement de clic sur le bouton.

        Args:
            touch (Touch): Objet représentant le toucher.

        Returns:
            bool: True si le bouton a été pressé, False sinon.
        """
        if self.collide_point(*touch.pos):
            self.is_pressed = True
            return super().on_touch_down(touch)
        return False

    def on_mouse_move(self, window, pos):
        """Détecte si la souris survole le bouton.

        Args:
            window (Window): Fenêtre actuelle.
            pos (tuple): Position actuelle de la souris (x, y).
        """
        self.is_hovered = self.collide_point(*pos)

    def on_touch_up(self, touch):
        """Gère l'événement de relâchement du bouton.

        Args:
            touch (Touch): Objet représentant le toucher.

        Returns:
            bool: True si l'événement a été traité, False sinon.
        """
        if self.is_pressed:
            self.is_pressed = False
        return super().on_touch_up(touch)


class CWButtonCancel(ButtonTheme):
    """Bouton d'annulation."""


class CWButtonOK(ButtonTheme):
    """Bouton de validation."""


class ButtonYes(ButtonTheme):
    """Bouton pour une confirmation positive."""


class ButtonNo(ButtonTheme):
    """Bouton pour une confirmation négative."""
