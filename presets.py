import flet as ft


class WarningMsg(ft.Text):
    def super(self, value: str):
        return ft.Text(value=value,
                       size=24,
                       weight=ft.FontWeight.W_100,
                       italic=True
                       )


# class DropDownLang(ft.Dropdown):
#     def super(self, label: str, on_change: Any):
#         return ft.Dropdown(
#             options=[ft.dropdown.Option(lang) for lang in LANGUAGES],
#             label=label,
#             on_change=on_change
#         )
