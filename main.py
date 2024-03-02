from presets import *
from openai_algorithm import get_completion_elements, LANGUAGES

import flet as ft
import os

FROM_LANGUAGE_NAME = ""
TO_LANGUAGE_NAME = ""
WARNINGS_COUNTER = 0
DO_INCREMENT = True

def main(page: ft.Page):
    global FROM_LANGUAGE_NAME
    global TO_LANGUAGE_NAME
    global WARNINGS_COUNTER

    page.scroll = ft.ScrollMode.ALWAYS
    page.fonts = {
        "RobotoSlab": "fonts/RobotoSlab[wght].ttf"
    }
    page.theme = ft.Theme(font_family="RobotoSlab")
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    intro_large_text = ft.Text(
        value="Hello, dear User!\n"
              "Welcome to programming languages converter",
        style=ft.TextThemeStyle.DISPLAY_MEDIUM,
        weight=ft.FontWeight.W_300,
        text_align=ft.TextAlign.CENTER
    )
    intro_large_cursive_text = ft.Text(
        value="(and vice versa)",
        size=24,
        weight=ft.FontWeight.W_100,
        italic=True
    )

    # from_language_choose = ft.Text(
    #     value=f"from {FROM_LANGUAGE_NAME}",
    #     italic=True,
    # )
    #
    # to_language_choose = ft.Text(
    #     value=f"to {TO_LANGUAGE_NAME}",
    #     italic=True,
    # )

    def from_lang_choose(e):
        global FROM_LANGUAGE_NAME
        print(f"Dropdown: {from_language_choose.value}")
        FROM_LANGUAGE_NAME = from_language_choose.value
        code_field.label = f"your {FROM_LANGUAGE_NAME} code here"
        page.update()

    def to_lang_choose(e):
        global TO_LANGUAGE_NAME
        print(f"Dropdown: {to_language_choose.value}")
        TO_LANGUAGE_NAME = to_language_choose.value
        page.update()

    from_language_choose = ft.Dropdown(
        options=[ft.dropdown.Option(lang) for lang in LANGUAGES],
        label="FROM",
        on_change=from_lang_choose
    )

    to_language_choose = ft.Dropdown(
        options=[ft.dropdown.Option(lang) for lang in LANGUAGES],
        label="TO",
        on_change=to_lang_choose
    )

    code_field = ft.TextField(
        label=f"your {FROM_LANGUAGE_NAME}code here",
        width=750,
        text_align=ft.TextAlign.LEFT,
        multiline=True,
    )

    translated_code = ft.Text(
        value='',
        size=19,
        text_align=ft.TextAlign.START,
        selectable=True
    )

    def toggle_icon_button(e):
        global FROM_LANGUAGE_NAME
        global TO_LANGUAGE_NAME

        temp = to_language_choose.value
        to_language_choose.value = from_language_choose.value
        from_language_choose.value = temp

        FROM_LANGUAGE_NAME = from_language_choose.value
        TO_LANGUAGE_NAME = to_language_choose.value
        if not FROM_LANGUAGE_NAME:
            code_field.label = "your code here"
        else:
            code_field.label = f"your {FROM_LANGUAGE_NAME} code here"
        page.update()

    def remove_warning_msgs(*msgs):
        global WARNINGS_COUNTER
        WARNINGS_COUNTER = 0
        for msg in msgs:
            if msg in warnings_list:
                warnings_list.remove(msg)

    def translate_code_command(e):
        global FROM_LANGUAGE_NAME
        global TO_LANGUAGE_NAME
        global WARNINGS_COUNTER
        global DO_INCREMENT

        print(TO_LANGUAGE_NAME, FROM_LANGUAGE_NAME)
        print(to_language_choose.value, from_language_choose.value)

        empty_code_field_response_msg.disabled = True
        empty_code_field_response_msg.visible = False
        unclear_code_response_msg.disabled = True
        unclear_code_response_msg.visible = False

        if to_language_choose.value == from_language_choose.value or (not to_language_choose.value) or (
                not from_language_choose.value):
            if (not to_language_choose.value) or (not from_language_choose.value):
                no_lang_msg.disabled = False
                no_lang_msg.visible = True
                if no_lang_msg not in warnings_list:
                    warnings_list.append(no_lang_msg)
            else:
                same_lang_msg.disabled = False
                same_lang_msg.visible = True
                no_lang_msg.disabled = True
                no_lang_msg.visible = False
                if same_lang_msg not in warnings_list:
                    warnings_list.append(same_lang_msg)

            print(DO_INCREMENT, warnings_list)
            if DO_INCREMENT:
                DO_INCREMENT = False
                WARNINGS_COUNTER += 1
                warnings_text.value = f"\nWarnings: {WARNINGS_COUNTER}\n"
        else:
            same_lang_msg.disabled = True
            same_lang_msg.visible = False
            no_lang_msg.disabled = True
            no_lang_msg.visible = False

            DO_INCREMENT = True
            if WARNINGS_COUNTER > 0:
                remove_warning_msgs(same_lang_msg, no_lang_msg, empty_code_field_response_msg, unclear_code_response_msg)
                warnings_text.value = f"\nWarnings: {WARNINGS_COUNTER}\n"
            if WARNINGS_COUNTER == 0:
                response = get_completion_elements(code_field.value, FROM_LANGUAGE_NAME, TO_LANGUAGE_NAME)
                print(f"Initial response: {response}")

                if isinstance(response, dict):
                    if response.get(1):
                        empty_code_field_response_msg.disabled = False
                        empty_code_field_response_msg.visible = True
                        empty_code_field_response_msg.value = response.get(1)
                        warnings_list.append(empty_code_field_response_msg)

                        WARNINGS_COUNTER += 1
                        warnings_text.value = f"\nWarnings: {WARNINGS_COUNTER}\n"
                    elif response.get(2):
                        unclear_code_response_msg.disabled = False
                        unclear_code_response_msg.visible = True
                        unclear_code_response_msg.value = response.get(2)
                        warnings_list.append(unclear_code_response_msg)

                        WARNINGS_COUNTER += 1
                        warnings_text.value = f"\nWarnings: {WARNINGS_COUNTER}\n"

                    print(warnings_list)
                elif isinstance(response, str):
                    translated_code.value = response
                else:
                    print(f"{code_field.value=}")
                    print(FROM_LANGUAGE_NAME, TO_LANGUAGE_NAME)
                    print(f"{response=}\n")
                    response_text: str = response[0]
                    translated_code.value = response_text[response_text.index("\n"):]

        page.update()

    def clear_code_field_command(e):
        code_field.value = ''
        page.update()

    translate_code_button = ft.TextButton(
        f"Translate to {TO_LANGUAGE_NAME}",
        on_click=translate_code_command,
        icon=ft.icons.TRANSLATE
    )

    clear_code_field_button = ft.TextButton(
        "Clear Code",
        on_click=clear_code_field_command,
        icon=ft.icons.DELETE
    )

    # show ChatGPT annotations (button)

    language_switch_icon = ft.IconButton(
        icon=ft.icons.COMPARE_ARROWS,
        on_click=toggle_icon_button,
        icon_color="blue400",
        icon_size=80
    )

    warnings_text = ft.Text(
        value=f"\nWarnings: {WARNINGS_COUNTER}\n",
        style=ft.TextThemeStyle.DISPLAY_SMALL,
        size=25,
        text_align=ft.TextAlign.CENTER,
        italic=True
    )

    same_lang_msg = WarningMsg(("Both languages are same!\n"
                                "Please, change one of them,\n"
                                "in order to conduct translation properly!\n"))

    no_lang_msg = WarningMsg(("Some of the languages are absent!\n"
                              "Please, fill all the gaps!\n"))

    empty_code_field_response_msg = WarningMsg("")

    unclear_code_response_msg = WarningMsg("")

    warnings_list = []

    main_stack = ft.ListView(
        [
            ft.Row(
                [
                    ft.Text(
                        value="In the gap below you can insert your initial code and then click on the switcher on the "
                              "right hand side in order to choose the conversion mode. This program checks firstly, "
                              "whether your code fits the requirements either Java or pseudo-code, "
                              "informs about the possible language recognition errors and then conducts the "
                              "conversion\n",
                        size=22,
                        text_align=ft.TextAlign.JUSTIFY,
                        expand=True
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Row(
                [
                    ft.Column(
                        [
                            code_field,
                            ft.Text(
                                value="Translated code:",
                                size=22
                            ),
                            translated_code
                        ],
                        spacing=30
                    ),
                    ft.Column(
                        [
                            ft.Column(
                                [
                                    from_language_choose
                                ],
                                width=300,
                            ),
                            ft.Row(
                                [
                                    language_switch_icon
                                ]
                            ),
                            ft.Row(
                                [
                                    to_language_choose
                                ],
                                width=200
                            ),
                            ft.Column(
                                [
                                    translate_code_button,
                                    clear_code_field_button,
                                    warnings_text,
                                    ft.Column(
                                        warnings_list
                                    )
                                ]
                            )
                        ],
                        spacing=22,
                        offset=ft.transform.Offset(0, 0.1)
                    )
                ],
                alignment=ft.MainAxisAlignment.START,
            ),

        ],
        width=1000,
        height=1000,
        auto_scroll=False
    )

    page.add(
        intro_large_text,
        intro_large_cursive_text,
        main_stack
    )

ft.app(target=main,
       view=None,
       port=int(os.getenv("PORT", 8502)),
      assets_dir="assets")
