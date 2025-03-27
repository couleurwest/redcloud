import toga
from toga.style import Pack

from redcloud_app.views.color_palette import ColorPalette


class HR(toga.Box):
    def __init__(self, height=2, color="gray"):
        super().__init__(style=Pack(flex=1, height=height, background_color=color, margin=10))

# 🔥 Création d'une classe LabelH1
class LabelH1(toga.Label):
    def __init__(self, text, color=ColorPalette.PRIMARY):
        super().__init__(
            text,
            style=Pack(font_size=18, color=color, font_weight="bold", margin=10)
        )# 🔥 Création d'une classe LabelH1

class LabelH2(toga.Label):
    def __init__(self, text, color=ColorPalette.SECONDARY, margin=10, **kwargs):
        super().__init__(
            text,
            style=Pack(font_size=16, color=color, font_weight="bold", margin=margin, **kwargs)
        )

class LabelH3(toga.Label):
    def __init__(self, text, color=ColorPalette.ACCENT, margin=10, **kwargs):
        super().__init__(
            text,
            style=Pack(font_size=14, color=color, font_weight="bold", margin=margin, **kwargs)
        )

class BoxView(toga.Box):
    main_window = None

    def __new__(cls, main_window, **kwargs):

        if not hasattr(cls, '_instance'):
            orig = super(BoxView, cls)
            cls._instance = orig.__new__(cls)
            cls._instance.main_window = main_window

        return cls._instance


    def delete_me(self):
        # Réinitialisation de l'instance
        type(self)._instance = None
