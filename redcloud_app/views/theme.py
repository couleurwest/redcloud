class ColorPalette:
    PRIMARY = (211/255, 47/255, 47/255, 1)
    SECONDARY = (0/255, 120/255, 212/255, 1)
    WHITE = (255/255, 255/255, 255/255, 1)
    LIGHT = (245/255, 245/255, 245/255, 1)
    HOVER_LIGHT = (1,1,1, 0.8)
    MEDIUM = (176/255, 176/255, 176/255, 0.3)
    DARK = (33/255, 33/255, 33/255, 1)
    ACCENT = (156/255, 27/255, 79/255, 1)
    LINK = (251/255, 192/255, 45/255, 1)
    ALERT_RED = (183/255, 28/255, 28/255, 1)
    SUCCESS_GREEN = (129/255, 199/255, 132/255, 1)
    WARNING_YELLOW = (255/255, 112/255, 67/255, 1)

    # Pour le thème sombre
    DARK_BACKGROUND = (18/255, 18/255, 18/255, 1)
    DARK_SURFACE = (40/255, 40/255, 40/255, 1)
    DARK_TEXT = (220/255, 220/255, 220/255, 1)
    DARK_BORDER = (80/255, 80/255, 80/255, 1)

class Theme:
    def __init__(self, primary, secondary, background, surface, hover, text_color, tertiary, accent, link, alert, success, warning):
        self.primary = primary
        self.secondary = secondary
        self.background = background
        self.surface = surface
        self.hover = hover
        self.text_color = text_color
        self.tertiary = tertiary
        self.accent = accent
        self.link = link
        self.alert = alert
        self.success = success
        self.warning = warning

class ThemeNormal(Theme):
    def __init__(self):
        super().__init__(
            primary=ColorPalette.PRIMARY,
            secondary=ColorPalette.SECONDARY,
            background=ColorPalette.LIGHT,
            hover=ColorPalette.HOVER_LIGHT,
            surface=ColorPalette.MEDIUM,
            text_color=ColorPalette.DARK,
            tertiary=ColorPalette.WHITE,
            accent=ColorPalette.ACCENT,
            link=ColorPalette.LINK,
            alert=ColorPalette.ALERT_RED,
            success=ColorPalette.SUCCESS_GREEN,
            warning=ColorPalette.WARNING_YELLOW
        )

class ThemeDark(Theme):
    def __init__(self):
        super().__init__(
            primary=ColorPalette.PRIMARY,
            secondary=ColorPalette.SECONDARY,
            background=ColorPalette.DARK_BACKGROUND,
            surface=ColorPalette.DARK_SURFACE,
            hover=ColorPalette.HOVER_LIGHT,
            text_color=ColorPalette.DARK_TEXT,
            tertiary=ColorPalette.DARK_BORDER,
            accent=ColorPalette.ACCENT,
            link=ColorPalette.LINK,
            alert=ColorPalette.ALERT_RED,
            success=ColorPalette.SUCCESS_GREEN,
            warning=ColorPalette.WARNING_YELLOW
        )
