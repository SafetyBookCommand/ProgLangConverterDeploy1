import re
from pprint import pprint
from typing import Any
from collections import deque

from errors import *
from constants import *

# NAME: (TYPE, VALUE)
VARIABLES = {}

# NAME: [IS_OPENED: bool, PROC_VARS: list] -> RETURN_COUNT can be 0 or 1
PROCEDURES = {}


# TAKEN FROM YT: https://www.youtube.com/watch?v=Eythq9848Fg&list=PLZQftyCk7_SdoVexSmwy_tBgs7P0b97yD&index=1


class Token:
    def __init__(self, type_, value: Any | None = None, line: int | None = None, col_st: int | None = None,
                 col_end: int | None = None):
        self.type_ = type_
        self.value = value
        self.line = line
        self.col_st = col_st
        self.col_end = col_end

    def __repr__(self):
        if self.type_ == UNKNOWN_TT:
            if self.value:
                return f"{self.type_}:{self.value}:{self.line}:{self.col_st}:{self.col_end}"
            return f"{self.type_}:{self.col_st}:{self.col_end}"
        if self.value:
            return f"{self.type_}:{self.value}"
        return f"{self.type_}"


class VarToken(Token):
    def __init__(self, name: str, type_: str | None = None, value: Any | None = None):
        super().__init__(type_, value)
        self.name = name

    def __repr__(self):
        if self.value:
            return f"{VAR_TT}-{self.name}:{self.type_}:{self.value}" if self.type_ else f"{VAR_TT}-{self.name}:{self.value}"
        return f"{VAR_TT}-{self.name}:{self.type_}" if self.type_ else f"{VAR_TT}-{self.name}"


class CurrentPoint:
    def __init__(self, line: int, col: int, idx: int):
        """
        :param line: starts from 0
        :param col: starts from 0
        """
        self.line = line
        self.col = col
        self.idx = idx

    def further(self, current_char):
        # check, whether we need to go to the next line
        if current_char == "\n":
            self.line += 1
            self.col = 0
        else:
            self.col += 1
        self.idx += 1

    def get_real_line(self):
        return self.line + 1

    def get_real_col(self):
        return self.col + 1

    def __copy__(self):
        return CurrentPoint(self.line, self.col, self.idx)


class Tokenizer:
    def __init__(self, txt: str, filename: str | None = None):
        self.txt = txt
        self.filename = filename

        self.pos = CurrentPoint(0, -1, -1)
        self.current_char = None
        self.further()

    def further(self):
        """
        go to the next character
        :return:
        """
        self.pos.further(self.current_char)
        self.current_char = self.txt[self.pos.idx] if self.pos.idx < len(self.txt) else None

    def make_num(self) -> Token | tuple[list, IllegalCharError]:
        """

        :return: Token
        """
        # num_str = ''
        dots = 0
        return_vals = [INT_TT, '']
        # print(f"{self.current_char=}")
        while (self.current_char is not None) and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                dots += 1
                if dots < 2:  # there can be one and only one dot in a float number
                    return_vals[1] += self.current_char
                    return_vals[0] = FLOAT_TT
                else:
                    return [], IllegalCharError(f"Wrong float number notation: {return_vals[1]}...!\n"
                                                f"There cannot be > 1 dots in a float number!",
                                                self.pos.line, self.pos.col, self.filename)
            else:
                return_vals[1] += self.current_char
                # print(f"{return_vals=}")
            self.further()

        return Token(return_vals[0], return_vals[1])

    def make_string(self) -> Token | tuple[list, IncorrectStringFormatError]:
        string_word = ''
        string_line = self.pos.line
        string_col_st = self.pos.col + 1  # + 1 ?
        self.further()
        while self.current_char != '"':
            match self.current_char:
                case "\n":
                    return [], IncorrectStringFormatError(f"String word: {string_word}", string_line,
                                                          string_col_st, self.pos.get_real_col(),
                                                          self.filename)
                case "\\":
                    self.further()
                    if self.current_char not in ('n', 't', '"', "\\"):
                        return [], IncorrectStringFormatError(f"String word: {string_word}",
                                                              string_line,
                                                              string_col_st, self.pos.get_real_col(),
                                                              self.filename)
                    #       ONLY \n WILL BE AVAILABLE FROM THE ENTIRE LIST OF PYTHON SPECIAL CHARS
                    if self.current_char == 'n':
                        self.current_char = "\n"

            string_word += self.current_char
            self.further()

        # print(f"{string_word=}")
        return Token(STRING_TT, string_word)

    @staticmethod
    def check_var(str_: str) -> bool:
        return bool(re.match(r"UNKNOWN:[A-Z][A-Z0-9_]*:.+", str_))

    @staticmethod
    def syntax_errors(var_value_mask: list, i: int, row_tokens_str: list[str], PROCEDURES: dict, var_value=None) -> bool:
        if var_value_mask[i] != '#':
            syntax_err1 = (var_value_mask[i - 1] == var_value_mask[i] == "func" or var_value_mask[i - 1] ==
                          var_value_mask[
                              i] == "funct" or var_value_mask[i - 1] == var_value_mask[i] == "def" or
                           var_value_mask[i - 1] == var_value_mask[i] == "comma")
            syntax_err2 = (var_value_mask[i - 1] == var_value_mask[i] == "op") or (
                    i == len(row_tokens_str) - 1 and var_value_mask[i] == "op")
            syntax_err3 = (var_value_mask[i - 1] == "lp" and var_value_mask[i] == "op") or (
                    var_value_mask[i - 1] == "op" and var_value_mask[i] == "rp")
            syntax_err4 = var_value_mask[i - 1] == "func" and var_value_mask[i] in ("rp", "op", "func")
            syntax_err5 = var_value_mask[i] == "end"
            syntax_err6 = var_value_mask[i] in ("loop", "while") and i != 1  # loop can take 0, 1; while - only 1
            syntax_err7 = var_value_mask[i] == "then" and i != len(var_value_mask) - 1
            syntax_err8 = (var_value_mask[i] == "from" and i != 2) or var_value_mask[i] == "else"
            syntax_err10 = var_value_mask[i - 1] in masks_to_exclude and var_value_mask[i] == var_value_mask[i - 1]
            syntax_err11 = (var_value_mask[i - 1] in ("from", "to", "loop", "while") and var_value_mask[i] in (
                "if", "else", "elif", "then")) or (
                                   var_value_mask[i] in ("from", "to", "loop", "while") and var_value_mask[i - 1] in (
                               "if", "else", "elif", "then"))
            try:
                syntax_err9 = (var_value_mask[i] not in ("var", "while") and (
                            row_tokens_str[i].split(':')[1] not in PROCEDURES) and i == 1) and var_value_mask[
                                  i - 1] == "loop"
                syntax_err12 = var_value_mask[i - 1] == "to" and (
                        ("STRING" in row_tokens_str[i - 2] or "STRING" in row_tokens_str[i]) or (
                        var_value_mask[i - 2] not in ("funct", "var") or var_value_mask[i] not in ("funct", "var")))
                syntax_err13 = (var_value_mask[i] == 'rp' and var_value_mask[i - 1] == 'lp') and (
                        var_value_mask[i - 2] != "func" and row_tokens_str[i - 2] != "OUTPUT")
            except IndexError:
                syntax_err9 = syntax_err12 = syntax_err13 = False
            syntax_err14 = var_value_mask[i] == "comma" and (var_value_mask[i - 1] not in ("var", "rp", "funct"))
            syntax_err15 = var_value_mask[i] == "rp" and var_value_mask[i - 1] == "comma"

            if var_value is not None:
                syntax_var_err = i == len(var_value) - 1 and var_value_mask[i] in ("func", "op")
                return syntax_err1 or syntax_err2 or syntax_err3 or syntax_err4 or syntax_err5 or syntax_err6 or syntax_err7 or syntax_err8 or syntax_err9 or syntax_err10 or syntax_err11 or syntax_err12 or syntax_err13 or syntax_err14 or syntax_err15 or syntax_var_err
            return syntax_err1 or syntax_err2 or syntax_err3 or syntax_err4 or syntax_err5 or syntax_err6 or syntax_err7 or syntax_err8 or syntax_err9 or syntax_err10 or syntax_err11 or syntax_err12 or syntax_err13 or syntax_err14 or syntax_err15
        return False

    def make_tokens(self) -> tuple:
        row_tokens = []
        tokens = []
        AS_count = 0
        is_comment = False
        procedures_init_in_row = 0
        comment = ''

        returns_count = 0
        procedures_count_now = 0
        # QUEUE USAGE!!!!
        procedures_queue = deque()

        while self.current_char is not None:
            row_tokens_str = list(map(str, row_tokens))
            if is_comment:
                match self.current_char:
                    case "\n":
                        is_comment = False
                        row_tokens.append(Token(COMMENT_TT, comment))
                        # print(f"{row_tokens=}")
                        comment = ''
                    case _:
                        comment += self.current_char
                        self.further()
            else:
                match self.current_char:
                    case "\n":
                        # print(f"INIT: {row_tokens_str=}")
                        if row_tokens_str:
                            check_unknown = list(filter(re.compile(r"UNKNOWN:.+").match,
                                                        row_tokens_str))  # https://stackoverflow.com/questions/33883512/check-if-all-characters-of-a-string-are-uppercase # https://stackoverflow.com/questions/33883512/check-if-all-characters-of-a-string-are-uppercase
                            var_value_mask = []
                            # print(f"{row_tokens=} || {check_unknown=}")
                            if row_tokens and check_unknown:
                                if "AS" in row_tokens_str:
                                    for special_token in SPECIAL_TOKENS_TO_EXCLUDE_FOR_VAR:
                                        if special_token in row_tokens_str:
                                            # print(f"{row_tokens_str}")
                                            return [], KeyWordError(f"Wrong usage of {special_token}!",
                                                                    self.pos.line, self.pos.col, self.pos.col,
                                                                    self.filename)
                                    var = row_tokens_str[0]
                                    _, var_name, var_line, var_col_st, var_col_end = var.split(':')
                                    # print(f"VAR: {var}")
                                    if self.check_var(var):
                                        if var_name not in VARIABLES:
                                            VARIABLES[var_name] = ''  # for initialization
                                        var_value = row_tokens[2:-1] if list(filter(re.compile(r"COMMENT:.+").match,
                                                                                    row_tokens_str)) else row_tokens[2:]
                                        # print(f"VAR_VAL: {var_value}")
                                        row_tokens[0] = VarToken(var_name)

                                        if var_value:
                                            # print(f"{var=} || {var_value=}")
                                            updated_var_value = []
                                            for i, var_value_unknown in enumerate(var_value):
                                                if var_value_unknown.type_ == UNKNOWN_TT:
                                                    _, val, line, col_st, col_end = str(var_value_unknown).split(':')
                                                    if self.check_var(str(var)):
                                                        if val in VARIABLES and VARIABLES.get(val):
                                                            # print(val)
                                                            if i != 0 and var_value_mask[i - 1] == "var":
                                                                return [], IncorrectSyntaxError(
                                                                    f"Duplicated variable {val}!",
                                                                    line, col_st, col_end)
                                                            var_value_mask.append("var")
                                                            # print(VARIABLES, i, var_value)
                                                            assigned_var_value = VARIABLES.get(val)
                                                            row_tokens[i + 2] = VarToken(val,
                                                                                         assigned_var_value)  # i + 2 !!!
                                                            updated_var_value.append(row_tokens[i + 2])
                                                        else:
                                                            # print(procedures_queue)
                                                            current_procedure_variables = \
                                                            PROCEDURES[procedures_queue[-1]][1]
                                                            # print(f"\n{current_procedure_variables=} {val}\n")
                                                            if "VAR-" + val in list(map(str, current_procedure_variables)):
                                                                # print(f"VAL inside Proc: {val}")

                                                                if i != 0 and var_value_mask[i - 1] == "var":
                                                                    return [], IncorrectSyntaxError(
                                                                        f"Duplicated variable {val}!",
                                                                        line, col_st, col_end)
                                                                var_value_mask.append("var")
                                                                row_tokens[i + 2] = VarToken(val)
                                                                updated_var_value.append(row_tokens[i + 2])
                                                                PROCEDURES[procedures_queue[-1]][1].append(
                                                                    VarToken(val))
                                                            else:
                                                                if row_tokens_str[i - 1] == "LOOP":
                                                                    if procedures_count_now == 0:
                                                                        VARIABLES[val] = ''
                                                                    else:
                                                                        PROCEDURES[procedures_queue[-1]][1].append(
                                                                            VarToken(val))
                                                                else:
                                                                    return [], UsingVariableBeforeAssignmentError(
                                                                        f"Name: {val}", line, col_st, col_end,
                                                                        self.filename)

                                                    else:
                                                        # if var_name in VARIABLES
                                                        return [], IncorrectVariableCommandNameError(
                                                            f"Name: {var_name}",
                                                            var_line, var_col_st,
                                                            var_col_end)
                                                elif var_value_unknown.type_ != COMMENT_TT:
                                                    # print(var_value_unknown.type_)
                                                    if var_value_unknown.type_ in EXIST_IN_PYTHON:
                                                        var_value_mask.append(
                                                            EXIST_IN_PYTHON.get(var_value_unknown.type_)[1])
                                                    elif var_value_unknown.type_ in DONT_EXIST_IN_PYTHON:
                                                        var_value_mask.append(
                                                            DONT_EXIST_IN_PYTHON.get(var_value_unknown.type_)[1])
                                                    updated_var_value.append(var_value_unknown)

                                                    if var_value_mask[0] == "op":
                                                        return [], IncorrectSyntaxError("Syntax Error!",
                                                                                        self.pos.get_real_line(), self.pos.col,
                                                                                        self.pos.col, self.filename)
                                                    if i != 0:

                                                        # add afterwards errors, related to special keywords!!!!
                                                        if self.syntax_errors(var_value_mask, i, row_tokens_str,
                                                            PROCEDURES, var_value) or \
                                                                var_value_mask[i] == "func":
                                                            return [], IncorrectSyntaxError("Syntax Error!",
                                                                                            self.pos.get_real_line(),
                                                                                            self.pos.col, self.pos.col,
                                                                                            self.filename)
                                            VARIABLES[var_name] = updated_var_value

                                            # print(var_value_mask)
                                        else:
                                            return [], IncorrectAssignError("Nothing has been assigned!", self.pos.line,
                                                                            self.pos.col, self.pos.col)
                                    else:
                                        return [], IncorrectVariableCommandNameError(f"Name: {var_name}", var_line,
                                                                                     var_col_st, var_col_end)
                            if (not check_unknown) or "AS" not in row_tokens_str:
                                # print(f"{row_tokens_str=}")
                                for i, var_value_unknown in enumerate(row_tokens):
                                    # print(var_value_unknown, type(var_value_unknown))
                                    if var_value_unknown.type_ == UNKNOWN_TT:
                                        _, val, line, col_st, col_end = str(var_value_unknown).split(':')
                                        if self.check_var(str(var_value_unknown)):
                                            # print(f"CHECKED {procedures_count_now}")
                                            if val in VARIABLES and VARIABLES.get(val):
                                                var_value_mask.append("var")
                                                assigned_var_value = VARIABLES.get(val)
                                                row_tokens[i] = VarToken(val, assigned_var_value)
                                            elif val in PROCEDURES or procedures_count_now > 0:
                                                # print("VAL:" + val)
                                                # print("row:" + row_tokens_str[0])
                                                if row_tokens_str[
                                                    0] == "PROCEDURE":  # initialization of a procedure variable
                                                    PROCEDURES[procedures_queue[-1]][1].append(VarToken(val))
                                                    # print(PROCEDURES[procedures_queue[-1]][2])
                                                # else:
                                                #     row_tokens.append(VarToken(val))
                                                var_value_mask.append("var")
                                                row_tokens[i] = VarToken(val)
                                            else:
                                                return [], UsingVariableBeforeAssignmentError(f"Name: {val}",
                                                                                              line, col_st, col_end)
                                        else:
                                            if val in VARIABLES and val in PROCEDURES:
                                                var_value_mask.append("var")
                                                row_tokens[i] = Token(PROCNAME_TT, val)
                                            else:
                                                return [], IncorrectVariableCommandNameError(f"Name: {val}", line,
                                                                                             col_st, col_end)
                                    else:
                                        # print(var_value_unknown.type_)
                                        if var_value_unknown.type_ in EXIST_IN_PYTHON:
                                            var_value_mask.append(EXIST_IN_PYTHON.get(var_value_unknown.type_)[1])
                                        elif var_value_unknown.type_ in DONT_EXIST_IN_PYTHON:
                                            var_value_mask.append(DONT_EXIST_IN_PYTHON.get(var_value_unknown.type_)[1])

                                    if var_value_mask:
                                        # print(var_value_mask, row_tokens_str, i)
                                        match var_value_mask[0]:
                                            case "op":
                                                return [], IncorrectSyntaxError("Syntax Error!", self.pos.get_real_line(),
                                                                                self.pos.col, self.pos.col,
                                                                                self.filename)
                                            case "from" | "to" | "then" | "while":
                                                return [], KeyWordError(f"Key-word: {var_value_mask[0]}", self.pos.line,
                                                                        self.pos.col, self.pos.col, self.filename)
                                        if i != 0:
                                            # add afterwards errors, related to special keywords!!!!
                                            if self.syntax_errors(var_value_mask, i, row_tokens_str, PROCEDURES):
                                                return [], IncorrectSyntaxError("Syntax Error!",
                                                                                self.pos.get_real_line(), self.pos.col,
                                                                                self.pos.col, self.filename)

                            # print(f"MASK: {var_value_mask=}")

                            if var_value_mask.count("lp") != var_value_mask.count("rp"):
                                return [], IncorrectSyntaxError("There is a problem with the parentheses!",
                                                                self.pos.get_real_line(), self.pos.col, self.pos.col,
                                                                self.filename)
                            if ("if" in var_value_mask or "elif" in var_value_mask) and (
                                    "end" not in var_value_mask) and ("then" not in var_value_mask):
                                return [], KeyWordError("then", self.pos.line,
                                                        self.pos.col, self.pos.col, self.filename)

                        #  check whether there is no FormatIncompatibilityError
                        if len(row_tokens) >= 3:
                            OP_TO_FILTER = (PLUS_TT, MINUS_TT, MULTIPLY_TT, DIVIDE_TT, DIV_TT, MOD_TT, DIV_TT, GT_TT,
                                            ST_TT, GTEQ_TT, STEQ_TT)
                            token_types = [token_.type_ for token_ in row_tokens if
                                           token_.type_ not in (LEFT_PARENT_TT, RIGHT_PARENT_TT)]
                            for i in range(1, len(token_types)):
                                if token_types[i] in OP_TO_FILTER:
                                    # print(f"{token_types=}")
                                    try:
                                        incompatibility_error1 = (token_types[i - 1] == STRING_TT or "[STRING" in str(
                                            token_types[i - 1])) and token_types[
                                                                     i + 1] in (INT_TT, FLOAT_TT)
                                        incompatibility_error2 = (token_types[i + 1] == STRING_TT or "[STRING" in str(
                                            token_types[i + 1])) and token_types[
                                                                     i - 1] in (INT_TT, FLOAT_TT)
                                        incompatibility_error3 = token_types[i] in OP_TO_FILTER[1:] and token_types[
                                            i - 1] == STRING_TT and token_types[i + 1] == STRING_TT
                                        if incompatibility_error1 or incompatibility_error2 or incompatibility_error3:
                                            return [], FormatIncompatibilityError(
                                                f"Elements: {token_types[i - 1]} {token_types[i]} {token_types[i + 1]}",
                                                self.pos.line, self.pos.col,
                                                self.pos.col, self.filename)
                                    except IndexError:
                                        ...
                                        # print("\nHERE COULD BE INDEX_ERROR!\n")

                        # print(row_tokens)
                        tokens.append(row_tokens)
                        AS_count = 0
                        row_tokens = []
                        # is_procedure_row = False
                        self.further()
                    case self.current_char if self.current_char in DIGITS:
                        num = self.make_num()
                        if isinstance(num, Token):
                            row_tokens.append(num)
                        else:
                            return num
                    case '"':
                        current_string = self.make_string()
                        if isinstance(current_string, Token):
                            row_tokens.append(current_string)
                            self.further()
                        else:
                            return current_string
                    case "\t" | ' ':
                        self.further()
                    case '+':
                        row_tokens.append(Token(PLUS_TT))
                        self.further()
                    case '-':
                        row_tokens.append(Token(MINUS_TT))
                        self.further()
                    case '*':
                        row_tokens.append(Token(MULTIPLY_TT))
                        self.further()
                    case '/':
                        self.further()
                        if self.current_char == '/':
                            is_comment = True
                            self.further()
                        else:
                            row_tokens.append(Token(DIVIDE_TT))
                    case '(':
                        # print(row_tokens)
                        if row_tokens[-1].type_ == PROCNAME_TT:
                            procedures_init_in_row += 1
                        row_tokens.append(Token(LEFT_PARENT_TT))
                        self.further()
                    case ')':
                        row_tokens.append(Token(RIGHT_PARENT_TT))
                        self.further()
                    case '=':
                        self.further()
                        if self.current_char == '=':
                            row_tokens.append(Token(EQ_TT))
                            self.further()
                        else:

                            AS_count += 1
                            if AS_count > 1:
                                return [], IncorrectAssignError("There are more than 1 '=' char!", self.pos.line,
                                                                self.pos.col, self.pos.col)
                            if "AS" in row_tokens_str and row_tokens_str.index("AS") != 1:
                                return [], IncorrectAssignError("'=' is at a wrong position!", self.pos.line,
                                                                self.pos.col, self.pos.col)
                            row_tokens.append(Token(AS_TT))
                    case '>':
                        self.further()
                        if self.current_char == '=':
                            row_tokens.append(Token(GTEQ_TT))
                            self.further()
                        else:
                            row_tokens.append(Token(GT_TT))
                    case '<':
                        self.further()
                        if self.current_char == '=':
                            row_tokens.append(Token(STEQ_TT))
                            self.further()
                        else:
                            row_tokens.append(Token(ST_TT))
                    case '!':
                        self.further()
                        if self.current_char == '=':
                            row_tokens.append(Token(NEQ_TT))
                            self.further()
                        else:
                            return [], IncorrectSyntaxError("Wrong usage of '!'", self.pos.line, self.pos.col,
                                                            self.pos.col, self.filename)
                    case ',':
                        if procedures_init_in_row > 0:
                            row_tokens.append(Token(COMMA_TT))
                            self.further()
                        else:
                            return [], IncorrectSyntaxError("Comma in Wrong Place!", self.pos.get_real_line(),
                                                            self.pos.col, self.pos.get_real_col(), self.filename)
                    case _:
                        word = ''
                        line = self.pos.get_real_line()
                        col_st = self.pos.col + 1
                        col_end = self.pos.col
                        char = self.current_char
                        # print(f"{char=} || {col_st=} || {self.pos.line}")

                        while char is not None and (char not in (' ', "\n", "\t", '(', ')', ',')):
                            word += char
                            col_end += 1

                            self.further()  # !
                            char = self.current_char

                        match word:
                            case "output":
                                if len(row_tokens) == 0:
                                    row_tokens.append(Token(OUTPUT_TT))
                                    self.further()
                                else:
                                    return [], IncorrectOutputPositionError(f"'{word}'", self.pos.line, col_st, col_end,
                                                                            self.filename)
                            case "mod":
                                row_tokens.append(Token(MOD_TT))
                                self.further()
                            case "div":
                                row_tokens.append(Token(DIV_TT))
                                self.further()
                            #     VARIABLES SECTION:
                            case "AND":
                                row_tokens.append(Token(AND_TT))
                                self.further()
                            case "OR":
                                row_tokens.append(Token(OR_TT))
                                self.further()
                            case "NOT":
                                row_tokens.append(Token(NOT_TT))
                                self.further()
                            # TRANSFER THESE PARTS OF THE CODE BELOW TO THE SEPARATE METHODS!
                            case "end":
                                row_tokens.append(Token(END_TT))
                                self.further()
                            case "if":
                                if len(row_tokens) == 1 and str(row_tokens[0]) == "ELSE":
                                    row_tokens[0] = Token(ELSEIF_TT)
                                else:
                                    row_tokens.append(Token(IF_TT))

                                self.further()
                            case "else":
                                row_tokens.append(Token(ELSE_TT))
                                # self.further()
                            case "then":
                                row_tokens.append(Token(THEN_TT))
                            case "loop":
                                row_tokens.append(Token(LOOP_TT))
                            case "while":
                                row_tokens.append(Token(WHILE_TT))
                                self.further()
                            case "from":
                                row_tokens.append(Token(FROM_TT))
                                self.further()
                            case "to":
                                try:
                                    for_loop_var = row_tokens_str[1].split(':')[1]
                                    for_loop_var_val = row_tokens_str[3].split(':')[1]
                                    for_loop_var_type = row_tokens_str[3].split(':')[0]
                                    if for_loop_var_type != "INT":
                                        return [], NotIntegerInForLoopError(f"Type Given: {for_loop_var_type}",
                                                                            self.pos.line, None, None,
                                                                            self.filename)
                                    # print(f"{for_loop_var=} | {for_loop_var_val=} | {row_tokens_str}")
                                    if for_loop_var not in VARIABLES:
                                        VARIABLES[for_loop_var] = [Token(INT_TT, for_loop_var_val)]
                                    else:
                                        return [], VariableInLoopError(f"Same Variable {for_loop_var}",
                                                                       self.pos.get_real_line(), None,
                                                                       None, self.filename)
                                    row_tokens.append(Token(TO_TT))
                                    self.further()
                                except IndexError:  # it always appears, when there is anything but a variable between loop and from
                                    return [], VariableInLoopError("Variable was not detected!",
                                                                   self.pos.get_real_line(), None, None,
                                                                   self.filename),
                            case "procedure":
                                if row_tokens and str(row_tokens[0]) == "END":
                                    try:
                                        PROCEDURES[procedures_queue[-1]][0] = False
                                    except IndexError:
                                        return [], KeyWordError("Incorrect Procedure Assignment!",
                                                                self.pos.get_real_line(), None, None,
                                                                self.filename)
                                    # print(procedures_queue)
                                    procedures_queue.pop()
                                    procedures_count_now -= 1
                                    row_tokens.append(Token(PROCEDURE_TT))
                                    if procedures_count_now < 0:
                                        return [], KeyWordError("Incorrect Procedure Assignment!",
                                                                self.pos.get_real_line(), None, None,
                                                                self.filename)
                                else:
                                    procedure_name = ''
                                    procedure_line = self.pos.get_real_line()
                                    procedure_col_st = self.pos.get_real_col()
                                    while self.current_char != '(':
                                        if self.current_char == "\n" and len(row_tokens) == 0:
                                            return [], ProcedureInitializationError(
                                                f"Incorrect Procedure Name: {procedure_name}",
                                                procedure_line, procedure_col_st,
                                                self.pos.get_real_col(), self.filename)
                                        elif self.current_char in (' ', "\n"):
                                            self.further()
                                        else:
                                            procedure_name += self.current_char
                                            self.further()
                                    if not bool(re.match(r"[A-Za-z][A-Za-z0-9_]*\(", procedure_name + '(')):
                                        return [], ProcedureInitializationError(
                                            f"Incorrect Procedure Name: {procedure_name}",
                                            procedure_line, procedure_col_st,
                                            self.pos.get_real_col(), self.filename)
                                    if procedure_name in VARIABLES:
                                        return [], ProcedureInitializationError(
                                            f"There Is Already a Variable with the Same Name: {procedure_name}",
                                            procedure_line, procedure_col_st,
                                            self.pos.get_real_col(), self.filename)
                                    if procedure_name in PROCEDURES:
                                        return [], ProcedureInitializationError(
                                            f"There Is Already a Procedure with the Same Name: {procedure_name}",
                                            procedure_line, procedure_col_st,
                                            self.pos.get_real_col(), self.filename)

                                    procedures_count_now += 1
                                    PROCEDURES[procedure_name] = [True, []]  # for initialization
                                    procedures_queue.append(procedure_name)
                                    VARIABLES[procedure_name] = Token(PROCNAME_TT, procedure_name)
                                    row_tokens.append(Token(PROCEDURE_TT))
                                    row_tokens.append(Token(PROCNAME_TT, procedure_name))

                            case "return":
                                # if PROCEDURES[procedures_queue[-1]][0] == 1:
                                #     return [], KeyWordError("There can't be more than 1 'return' for each function",
                                #                             self.pos.get_real_line(), self.pos.get_real_col(),
                                #                             self.pos.get_real_col(), self.filename)

                                if procedures_count_now > 0:
                                    # PROCEDURES[procedures_queue[-1]][0] += 1
                                    returns_count += 1
                                    row_tokens.append(Token(RETURN_TT))
                                else:
                                    return [], KeyWordError("'return' is at wrong place!", self.pos.get_real_line(),
                                                            self.pos.get_real_col(), self.pos.get_real_col())
                            case _:
                                # print(f"Current: {word}")
                                row_tokens.append(Token(UNKNOWN_TT, word, line, col_st, col_end))

        if self.pos.idx == len(self.txt) or self.current_char == "\n":
            tokens.append(row_tokens)
            self.further()
        return tokens, None


class Compiler:
    filename = None

    def __init__(self, txt: str, filename: str | None = None, filepath: str | None = None, filepath_delimiter: str = '/'):
        self.txt = txt
        self.filename = filename
        self.filepath = filepath
        self.filepath_delimiter = filepath_delimiter

    def find_filename(self):
        if self.filepath is not None:
            filepath_split = self.filepath.split(self.filepath_delimiter)
            self.filename = filepath_split[-1]

    def run(self) -> tuple[list, IllegalCharError]:
        self.find_filename()
        tokenizer = Tokenizer(self.txt, self.filename)
        tokens, err = tokenizer.make_tokens()

        # print()
        # pprint(f"{VARIABLES=}")
        # print()

        return tokens, err
