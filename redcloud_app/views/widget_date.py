import toga
from toga.style import Pack
from toga.validators import MinLength, MaxLength
from datetime import datetime


class DateWidget(toga.Box):

    # Fonction de validation de la date
    @staticmethod
    def validate_date(day, month, year):
        try:
            # Créer la date à partir des champs de jour, mois et année
            return datetime(year, month, day)
        except ValueError:
            return False  # Non validée

    # Fonction de validation de la date
    @staticmethod
    def marge_year(value):
        try:
            year = int(value)
        except ValueError:
            return "Année invalide"

        today = datetime.today()
        maxy = today.year
        miny = year - 1

        return None if miny <= year <= maxy else "Année invalide"

    # Fonction de validation de la date
    @staticmethod
    def max_day(value):
        try:
            if int(value) > 31:
                raise ValueError()
        except ValueError:
            return "Jour invalide"

    @staticmethod
    def max_month(value):
        try:
            if int(value) > 12:
                raise ValueError()
        except ValueError:
            return "Mois invalide"

        return None

    def __init__(self, *args, **kwargs):

        self.__value = datetime.today()
        self.__is_valide = True

        # Champ de texte pour le jour
        self.day_input = toga.TextInput(
            value=str(self.__value.day),
            placeholder="DD",
            style=Pack(width=60, text_align="center"),
            on_change=self.on_change_date,
            validators = [ MinLength(1), MaxLength(2), DateWidget.max_day])

        # Champ de texte pour le mois
        self.month_input = toga.TextInput(
            value=str(self.__value.month),
            placeholder="MM",
            style=Pack(width=60 , text_align="center"),
            on_change=self.on_change_date,
            validators = [MinLength(1), MaxLength(2),DateWidget.max_month]
        )

        # Champ de texte pour l'année
        self.year_input = toga.TextInput(
            value=str(self.__value.year),
            placeholder="YYYY",
            style=Pack(width=75, text_align="center"),
            on_change=self.on_change_date,
            validators = [MinLength(4), MaxLength(4), DateWidget.marge_year ]
        )

        # Affichage du résultat de la validation
        self.result_label = toga.Label("", style=Pack(margin=10))

        # Organiser le layout
        self.box_date = toga.Box(
            children=[
                self.day_input,toga.Label('/', style=Pack(margin_left=5, margin_right=5, margin_top=10, margin_bottom=10)),
                self.month_input,toga.Label('/', style=Pack(margin_left=5, margin_right=5, margin_top=10, margin_bottom=10)),
                self.year_input,
            ],
            style=Pack(direction='row')
        )

        super().__init__(
            children=[ self.box_date, self.result_label ],
            style=Pack(direction='column', **kwargs)
        )

    @property
    def date_is_valid (self):
        # Vérifier si la date est valide après que le champ jour perde le focus
        day = int(self.day_input.value)
        month = int(self.month_input.value)
        year = int(self.year_input.value)
        self.__is_valide = False
        date_valid = DateWidget.validate_date(day, month, year)

        if not self.self.date_valid:
            self.result_label.text = "Date non invalide"
        else:
            self.__is_valide = True
            self.__value = date_valid

        return self.__is_valide

    def on_change_date(self, widget, **kwargs):
        # Si le champ jour est complet (2 caractères), passer au champ mois
        self.result_label.text = ""
        if widget.value:
            if not widget.value.isdigit():
                widget.value = ''
            else:
                if len(widget.value) >= 2 and self.date_is_valid:
                    index = self.box_date.index(widget) + 2
                    if index < len(self.box_date.children):
                        self.box_date.children[index].focus()

    @property
    def is_valid(self):
        return self.__is_valide

    @property
    def value(self):
        return self.__value

