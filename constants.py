# CONSTANTS
DIGITS = "0123456789"

INT_TT = "INT"
FLOAT_TT = "FLOAT"
STRING_TT = "STRING"
PLUS_TT = "PLUS"
MINUS_TT = "MINUS"
MULTIPLY_TT = "MUL"
DIVIDE_TT = "DIVIDE"  # not div! (/)
LEFT_PARENT_TT = "LPAR"  # (
RIGHT_PARENT_TT = "RPAR"  # )
MOD_TT = "MOD"  # %
DIV_TT = "DIV"  # //
EQ_TT = "EQ"  # ==
NEQ_TT = "NEQ"  # !=
GT_TT = "GT"  # >
ST_TT = "ST"  # <
GTEQ_TT = "GTEQ"  # >=
STEQ_TT = "STEQ"  # <=
AND_TT = "AND"  # and
OR_TT = "OR"  # or
NOT_TT = "NOT"  # not
COMMENT_TT = "COMMENT"

# SPECIAL
UNKNOWN_TT = "UNKNOWN"
AS_TT = "AS"  # =
VAR_TT = "VAR"
OUTPUT_TT = "OUTPUT"

END_TT = "END"

IF_TT = "IF"
ELSEIF_TT = "ELSEIF"
ELSE_TT = "ELSE"
THEN_TT = "THEN"

LOOP_TT = "LOOP"
WHILE_TT = "WHILE"

FROM_TT = "FROM"
TO_TT = "TO"

PROCEDURE_TT = "PROCEDURE"
PROCNAME_TT = "PROC"
RETURN_TT = "RETURN"
COMMA_TT = "COMMA"

SPECIAL_TOKENS_TO_EXCLUDE_FOR_VAR = (END_TT, IF_TT, ELSEIF_TT, ELSE_TT,
                                     THEN_TT, LOOP_TT, WHILE_TT, FROM_TT,
                                     TO_TT, PROCEDURE_TT)

# SPECIAL BLOCKS IDENTIFICATIONS (are set as key of block-dictionaries in Tokenizer):
IF_BLOCK = "IF_BLOCK"
ELSEIF_BLOCK = "ELSEIF_BLOCK"
ELSE_BLOCK = "ELSE_BLOCK"
LOOP_WHILE_BLOCK = "LOOP_WHILE_BLOCK"
LOOP_FOR_BLOCK = "LOOP_FOR_BLOCK"
PROCEDURE_BLOCK = "PROCEDURE_BLOCK"

# REVERSE CONST. MEANING (TOKEN -> PYTHON -> (python_element: str, meaning: str))
# "func" - Python built-in function (print())
# "funct" - Python function, which represents a type (int())
# "op" - Python operand (Ex.: +)
# "key" - Python keyword (Ex.: if, def, etc.)
# "var" - variable (in code)

EXIST_IN_PYTHON = {
    INT_TT: ("int", "funct"),
    FLOAT_TT: ("float", "funct"),
    STRING_TT: ("str", "funct"),
    PLUS_TT: ('+', "op"),
    MINUS_TT: ('-', "op"),
    MULTIPLY_TT: ('*', "op"),
    LEFT_PARENT_TT: ('(', "lp"),
    RIGHT_PARENT_TT: (')', "rp"),
    AS_TT: ('=', "op"),
    EQ_TT: ("==", "op"),
    NEQ_TT: ("!=", "op"),
    GT_TT: ('>', "op"),
    ST_TT: ('<', "op"),
    GTEQ_TT: (">=", "op"),
    STEQ_TT: ("<=", "op"),
    AND_TT: ("and", "op"),
    OR_TT: ("or", "op"),
    NOT_TT: ("not", "op"),
    IF_TT: ("if", "if"),
    ELSE_TT: ("else", "else"),
    WHILE_TT: ("while", "while"),
    COMMENT_TT: ('#', '#'),
    RETURN_TT: ("return", "return"),
    COMMA_TT: (',', "comma")
}

DONT_EXIST_IN_PYTHON = {
    MOD_TT: ("//", "op"),
    DIV_TT: ('%', "op"),
    OUTPUT_TT: ("print", "func"),
    END_TT: (None, "end"),
    ELSEIF_TT: ("elif", "elif"),
    THEN_TT: (None, "then"),
    LOOP_TT: (None, "loop"),
    FROM_TT: ("range", "from"),
    TO_TT: (None, "to"),
    PROCEDURE_TT: ("def", "def"),  # func?
    PROCNAME_TT: (None, "func")
}

masks_to_exclude = ("if", "else", "then", "end", "elif", "from", "loop", "to")

# IDENTIFICATION: (python_element: str, (value_lower_boundary, value_lower_boundary));
#                 None means till the end / from the start
IDENTIFICATIONS_TO_PYTHON = {
    IF_BLOCK: ("if", (1, -1)),
    LOOP_WHILE_BLOCK: ("while", (2, None)),
    LOOP_FOR_BLOCK: ("for", None),  # here is so specific Pseudocode syntax, so I will go through values of this block separately
    PROCEDURE_BLOCK: ("def", (1, None))
}