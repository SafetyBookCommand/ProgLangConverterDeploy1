import re
from pprint import pprint

from core import Token, VarToken
from constants import *
from errors import *


def add_sign_to_end(code_row, sign) -> str:
    return f"{code_row[:-1]}{sign}" if code_row[-1] == ' ' else f"{code_row}{sign}"


def to_python(tokens_list: list[list[Token | VarToken | str]], filename: str) -> str | None | Error:
    CODE_TO_EXECUTE = ''
    loop_count = 0  # must be even
    if_block_count = 0  # must be equal to end_if_count
    end_if_count = 0
    procedure_block_count = 0
    end_procedure_count = 0
    times_to_tab = 0  # how many times it is necessary to type \t before each line
    if_blocks_tabs = 0
    else_blocks = 0

    print_opened = False
    while_started = False
    procedure_opened = False

    for line_idx, row in enumerate(tokens_list):
        for col_idx, token in enumerate(row):
            if isinstance(token, VarToken):
                if str(row[col_idx - 1]) != "LOOP":
                    var_val = str(token).split('-')[1]
                    if ':' in var_val:
                        var_val = var_val.split(':')[0]
                    CODE_TO_EXECUTE += f"{var_val} "

            elif isinstance(token, Token):
                tt = token.type_
                t_val = token.value

                python_el = ''
                meaning = ''

                if tt in EXIST_IN_PYTHON:
                    python_el = EXIST_IN_PYTHON.get(tt)[0]
                    meaning = EXIST_IN_PYTHON.get(tt)[1]

                elif tt in DONT_EXIST_IN_PYTHON:
                    python_el = DONT_EXIST_IN_PYTHON.get(tt)[0]
                    meaning = DONT_EXIST_IN_PYTHON.get(tt)[1]
                
                match meaning:
                    case "funct":
                        typed_val = f"{python_el}(\"{t_val}\") " if python_el == "str" else f"{python_el}({t_val}) "
                        CODE_TO_EXECUTE += typed_val
                    case "op":
                        CODE_TO_EXECUTE += f"{python_el} "

                match tt:
                    case "LPAR":
                        CODE_TO_EXECUTE += python_el
                    case "RPAR":
                        CODE_TO_EXECUTE = add_sign_to_end(CODE_TO_EXECUTE, ") ")
                    case "IF":
                        if str(row[col_idx - 1]) == "END":
                            times_to_tab -= 1
                            end_if_count += 1
                        else:
                            CODE_TO_EXECUTE += f"{python_el} "
                            times_to_tab += 1
                            if_block_count += 1
                            if_blocks_tabs += 1
                    case "ELSEIF":
                        if if_blocks_tabs <= 0:
                            return CompilerIfBlockError(f"Token: {token}", line_idx + 1, None, None,
                                                        filename)
                        CODE_TO_EXECUTE = f"{CODE_TO_EXECUTE[:-1]}{python_el} "
                    case "ELSE":
                        else_blocks += 1
                        if else_blocks > if_blocks_tabs:
                            return CompilerIfBlockError(f"Token: {token}", line_idx + 1, None, None,
                                                        filename)
                        CODE_TO_EXECUTE = f"{CODE_TO_EXECUTE[:-1]}{python_el}:"
                    case "WHILE":
                        CODE_TO_EXECUTE += f"{python_el} "
                        while_started = True
                        loop_count += 1
                    case "LOOP":
                        if str(row[col_idx - 1]) == "END":
                            times_to_tab -= 1
                            loop_count += 1
                        else:
                            times_to_tab += 1
                    case "FROM":
                        for_var = str(row[1]).split('-')[1].split(':')[0]
                        lb = str(row[3]).split(':')[1]
                        rb = str(row[5]).split(':')[1]
                        CODE_TO_EXECUTE += "for " + for_var + " in range(" + lb + ", " + {rb} + " + 1): \n" + "\t" * times_to_tab
                        loop_count += 1
                        break
                    case "THEN":
                        CODE_TO_EXECUTE = f"{CODE_TO_EXECUTE[:-1]}: "
                    case "OUTPUT":
                        CODE_TO_EXECUTE += "print("
                        print_opened = True
                    case "COMMENT":
                        comment = f"#{token.value}"
                        if len(row) == 1:
                            CODE_TO_EXECUTE += comment
                        else:
                            CODE_TO_EXECUTE += f" {comment}"
                    case "PROCEDURE":
                        if str(row[col_idx - 1]) == "END":
                            times_to_tab -= 1
                            end_procedure_count += 1
                        else:
                            procedure_opened = True
                            procedure_block_count += 1
                            times_to_tab += 1
                            CODE_TO_EXECUTE += f"{python_el} "
                    case "PROC":
                        CODE_TO_EXECUTE += t_val
                    case "COMMA":
                        CODE_TO_EXECUTE += f"{python_el} "
                    case "RETURN":
                        CODE_TO_EXECUTE += f"{python_el} "
                        times_to_tab -= 1
                    case _:
                        ...
            else:
                return CompilerTokenError(f"Token: {token}", line_idx + 1, None, None, filename)
            if col_idx == len(row) - 1:
                if print_opened:
                    CODE_TO_EXECUTE = add_sign_to_end(CODE_TO_EXECUTE, ')')
                    print_opened = False
                if while_started:
                    CODE_TO_EXECUTE = add_sign_to_end(CODE_TO_EXECUTE, ':')
                    while_started = False
                if procedure_opened:
                    CODE_TO_EXECUTE = add_sign_to_end(CODE_TO_EXECUTE, ':')
                    procedure_opened = False

                CODE_TO_EXECUTE += "\n" + "\t" * times_to_tab

    # print("\n\nCODE:\n")
    if if_block_count != end_if_count:
        return CompilerIfBlockError("Some If-Block is not closed!", None, None, None, filename)
    if loop_count % 2 != 0:
        return CompilerWhileBlockError("Some While-Block is not closed!", None, None, None, filename)
    return CODE_TO_EXECUTE


def execute_python(code: str) -> None:
    try:
        exec(code)
    except Exception as e:
        print(f"PythonError: {e.args[0]}")
