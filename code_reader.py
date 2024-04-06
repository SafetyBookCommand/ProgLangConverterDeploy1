import io
import sys
from pprint import pprint

import core
import translator


def read_run(filename: str, txt: str | None = None, direct_from_files: bool = False, filepath: str | None = None) -> None | dict:
    output_parts = {
        "python_code": '',
        "output": '',
        "error": '',
        "filename": ''
    }
    if direct_from_files and filepath is not None:
        with open(filepath) as f:
            txt = f.read() + "\n"

    if txt:
        compiler = core.Compiler(txt, None, filepath) if direct_from_files else core.Compiler(txt, filename)
        output_parts["filename"] = compiler.filename
        res, err = compiler.run()

        string_io = io.StringIO()
        sys.stdout = string_io

        if err:
            print(err)
        else:
            python_code = translator.to_python(res, compiler.filename)
            output_parts["python_code"] = python_code
            print()
            translator.execute_python(python_code)

            output = string_io.getvalue()
            output_split = output.split("PythonError")
            if len(output_split) == 2:
                output_parts["error"] = f"PythonError{output_split[1]}"
            else:
                output_parts["output"] = output

        sys.stdout = sys.__stdout__
        return output_parts
    else:
        return


if __name__ == "__main__":
    pprint(read_run("/Users/cryptogazer/Desktop/IAs/ProgLangConverterDeploy1/CompilerFunctionality/test_prog2.txt"))
