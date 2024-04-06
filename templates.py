import flet as ft


class WarningMessage(ft.Text):
    def __init__(self, value):
        super().__init__(value)

    def __repr__(self):
        return ft.Text(
            value=self.value,
            theme_style=ft.TextThemeStyle.DISPLAY_SMALL,
            size=20,
            text_align=ft.TextAlign.JUSTIFY,
            expand=True
        )


class TextForCode(ft.Text):
    def __init__(self, size):
        super().__init__(size=size)

    def __repr__(self):
        return ft.Text(
            value='',
            size=self.size,
            text_align=ft.TextAlign.START,
            selectable=True
        )


class RightColumnLabels(ft.Text):
    def __init__(self, value):
        super().__init__(value)

    def __repr__(self):
        return ft.Text(
            value=self.value,
            theme_style=ft.TextThemeStyle.DISPLAY_SMALL,
            size=25,
            text_align=ft.TextAlign.CENTER,
            italic=True
        )
