import flet as ft

import os
from typing import Dict
from time import sleep

from code_reader import read_run

FROM_LANGUAGE_NAME = ""
TO_LANGUAGE_NAME = ""
DO_INCREMENT = True

filepath = ''
filename = ''
uf = []


def main(page: ft.Page):
    global FROM_LANGUAGE_NAME
    global TO_LANGUAGE_NAME
    global filename

    page.scroll = ft.ScrollMode.ALWAYS
    page.fonts = {
        "RobotoSlab": "fonts/RobotoSlab[wght].ttf"
    }
    page.theme = ft.Theme(font_family="RobotoSlab")
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    intro_large_text = ft.Text(
        value="Hello, dear User!\n"
              "Welcome to Pseudocode to Python Converter!",
        theme_style=ft.TextThemeStyle.DISPLAY_SMALL,
        weight=ft.FontWeight.W_300,
        text_align=ft.TextAlign.CENTER
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
    code_result = ft.Text(
            value='',
            size=22,
            text_align=ft.TextAlign.START,
            selectable=True
        )

    prog_bars: Dict[str, ft.ProgressRing] = {}
    files = ft.Ref[ft.Column]()
    upload_button = ft.Ref[ft.ElevatedButton]()

    def file_picker_result(e: ft.FilePickerResultEvent):
        upload_button.current.disabled = True if e.files is None else False
        prog_bars.clear()
        files.current.controls.clear()
        if e.files is not None:
            # if os.path.isdir("/app/uploads") and os.listdir("/app/uploads"):  
            #     for file in os.listdir("/app/uploads"):
            #         file_path_uploads = os.path.join("uploads", file)
            #         print(file_path_uploads)
            #         if os.path.isfile(file_path_uploads):
            #             os.remove(file_path_uploads)
            for f in e.files:
                prog = ft.ProgressRing(value=0, bgcolor="#eeeeee", width=20, height=20)
                prog_bars[f.name] = prog
                files.current.controls.append(ft.Row([prog, ft.Text(f.name)]))
        page.update()

    def on_upload_progress(e: ft.FilePickerUploadEvent):
        prog_bars[e.file_name].value = e.progress
        prog_bars[e.file_name].update()

    file_picker = ft.FilePicker(on_result=file_picker_result, on_upload=on_upload_progress)

    def upload_files(e):
        global filename
        global uf

        if file_picker.result is not None and file_picker.result.files is not None:
            try:
                os.mkdir("/app/uploads")
            except FileExistsError:
                print("exists")
            warnings_message.value = ''
            for f in file_picker.result.files:
                uf.append(
                    ft.FilePickerUploadFile(
                        f.name,
                        upload_url=page.get_upload_url(f.name, 600),
                    )
                )
                filename = f.name
            file_picker.upload(uf)
            
            print(f'ABSPATH: {os.path.abspath("uploads")}')
            print(os.listdir(os.path.abspath("uploads")))

            sleep(3)
            with open(f"/app/uploads/{filename}") as f:
                code_field.value = f.read()
            page.update()

    page.overlay.append(file_picker)

    select_button = ft.ElevatedButton(
            text="Select File",
            icon=ft.icons.FOLDER_OPEN,
            on_click=lambda _: file_picker.pick_files(allow_multiple=False),
        )

    files_col = ft.Column(ref=files)

    loader_button = ft.ElevatedButton(
            text="Upload",
            ref=upload_button,
            icon=ft.icons.UPLOAD,
            on_click=upload_files,
            disabled=True,
        )

    def translate_code_command(e):
        global filename
        global uf

        if not code_field.value:
            warnings_message.value = ("Your code field is empty! "
                                      "Maybe you have forgotten to upload "
                                      "your file?")

        else:
            warnings_message.value = ''
            pseudocode = code_field.value
            print("Pseudo:\n")
            print(pseudocode)
            output_dict = read_run(filename, pseudocode)
            print(output_dict)

            translated_code.value = output_dict["python_code"]
            code_result.value = output_dict["output"]
            warnings_message.value = output_dict["error"]
        page.update()

    def clear_code_field_command(e):
        code_field.value = ''
        warnings_message.value = ''
        page.update()

    translate_code_button = ft.TextButton(
        text="Translate to Python",
        on_click=translate_code_command,
        icon=ft.icons.TRANSLATE
    )

    clear_code_field_button = ft.TextButton(
        "Clear Code",
        on_click=clear_code_field_command,
        icon=ft.icons.DELETE
    )

    filename_text = ft.Text(
            value=f"\nFile: {filename}\n",
            theme_style=ft.TextThemeStyle.DISPLAY_SMALL,
            size=25,
            text_align=ft.TextAlign.CENTER,
            italic=True
        )
    warnings_text = ft.Text(
            value="Warnings:",
            theme_style=ft.TextThemeStyle.DISPLAY_SMALL,
            size=25,
            text_align=ft.TextAlign.CENTER,
            italic=True
        )
    warnings_message = ft.Text(
            value='',
            theme_style=ft.TextThemeStyle.DISPLAY_SMALL,
            size=20,
            text_align=ft.TextAlign.CENTER,
            width=200
        )

    main_stack = ft.ListView(
        [
            ft.Row(
                [
                    ft.Text(
                        value="In the gap below you can insert your initial code and then click on the button on the "
                              "right hand side in order to translate the pseudocode. This program checks firstly, "
                              "whether your code fits the requirements of IB-styled Pseudocode, "
                              "informs about the possible language errors. If there are no errors, it conducts the "
                              "conversion!\n\nSimple Rules:\n"
                              "\t1. Use rules of IB-Styled Pseudocode. Exceptions:\n"
                              "\t\t  1.1. \"Equals\" - \"==\"\n"
                              "\t\t  1.2. Special Chars: \\n, \\t can be typed only with double-slash: \\\\n, \\\\t\n"
                              "\t\t  1.3. You cannot write arguments of one function on multiple lines\n"
                              "\t\t  1.4. There are not available IB-Styled Pseudocode Data Structures\n"
                              "\t2. You can provide Pseudocode to the website by downloading your txt file or copying your code",
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
                            ft.Row(
                                [
                                    ft.Column(
                                        [
                                            ft.Text(
                                                value="Translated code:",
                                                size=22
                                            ),
                                            translated_code
                                        ],
                                        width=450
                                    ),
                                    ft.Column(
                                        [
                                            ft.Text(
                                                value="Result:",
                                                size=22
                                            ),
                                            code_result
                                        ],
                                        width=150,
                                        alignment=ft.MainAxisAlignment.END
                                    )
                                ],
                            )
                        ],
                        spacing=30
                    ),
                    ft.Column(
                        [
                            ft.Column(
                                [
                                    translate_code_button,
                                    clear_code_field_button,
                                    select_button,
                                    files_col,
                                    loader_button,
                                    filename_text,
                                    warnings_text,
                                    warnings_message
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
        main_stack
    )

ft.app(target=main,
       view=None,
       port=int(os.getenv("PORT", 8502)),
       assets_dir="assets",
       upload_dir="uploads")
