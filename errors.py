class Error:
    def __init__(self, err_name: str,
                 details,
                 line: int | None,
                 col_st: int | None,
                 col_end: int | None,
                 filename: str | None = None):
        self.err_name = err_name
        self.details = details
        self.line = line
        self.col_st = col_st
        self.col_end = col_end
        self.filename = filename

    def __str__(self):
        if (self.col_st is not None) and (self.col_end is not None):
            return (f"File: {self.filename} Line: {self.line} Col: {self.col_st}"
                    f"\n{self.err_name}: {self.details}") if self.col_st == self.col_end else (
                f"File: {self.filename} Line: {self.line} Col Start: {self.col_st} Col End: {self.col_end}"
                f"\n{self.err_name}: {self.details}"
            )
        if self.line:
            return (f"File: {self.filename} Line: {self.line}"
                    f"\n{self.err_name}: {self.details}")
        return (f"File: {self.filename}"
                f"\n{self.err_name}: {self.details}")


class IllegalCharError(Error):
    def __init__(self, details, line: int, col: int, filename: str | None = None):
        super().__init__("Illegal Character", details, line, col, col, filename)


class IllegalCommandError(Error):
    def __init__(self, details, line: int, col_st: int, col_end: int, filename: str | None = None):
        super().__init__("Illegal Command", details, line, col_st, col_end, filename)


class IncorrectOutputPositionError(Error):
    def __init__(self, details, line: int, col_st: int, col_end: int, filename: str | None = None):
        super().__init__("Incorrect Output Position", details, line, col_st, col_end, filename)


class IncorrectVariableCommandNameError(Error):
    def __init__(self, details, line: int, col_st: int, col_end: int, filename: str | None = None):
        super().__init__("Incorrect Variable or Command Name", details, line, col_st, col_end, filename)


class IncorrectAssignError(Error):
    def __init__(self, details, line: int, col_st: int, col_end: int, filename: str | None = None):
        super().__init__("Incorrect Assign Error", details, line, col_st, col_end, filename)


class UsingVariableBeforeAssignmentError(Error):
    def __init__(self, details, line: int, col_st: int, col_end: int, filename: str | None = None):
        super().__init__("Using Variable Before Assignment Error", details, line, col_st, col_end, filename)


class IncorrectSyntaxError(Error):
    def __init__(self, details, line: int, col_st: int, col_end: int, filename: str | None = None):
        super().__init__("Syntax Error", details, line, col_st, col_end, filename)


class IncorrectStringFormatError(Error):
    def __init__(self, details, line: int, col_st: int, col_end: int, filename: str | None = None):
        super().__init__("Incorrect String Format Error", details, line, col_st, col_end, filename)


class FormatIncompatibilityError(Error):
    def __init__(self, details, line: int, col_st: int, col_end: int, filename: str | None = None):
        super().__init__("Format Incompatibility Error", details, line, col_st, col_end, filename)


class KeyWordError(Error):
    def __init__(self, details, line: int, col_st: int | None, col_end: int | None, filename: str | None = None):
        super().__init__("Key-word Error", details, line, col_st, col_end, filename)


class VariableInLoopError(Error):
    def __init__(self, details, line: int, col_st: int | None, col_end: int | None, filename: str | None = None):
        super().__init__("Variable in Loop Error", details, line, col_st, col_end, filename)


class ProcedureInitializationError(Error):
    def __init__(self, details, line: int, col_st: int | None, col_end: int | None, filename: str | None = None):
        super().__init__("Procedure Initialization Error", details, line, col_st, col_end, filename)


class NotIntegerInForLoopError(Error):
    def __init__(self, details, line: int, col_st: int | None, col_end: int | None, filename: str | None = None):
        super().__init__("Boundaries are not integer!", details, line, col_st, col_end, filename)


class CompilerTokenError(Error):
    def __init__(self, details, line: int, col_st: int | None, col_end: int | None, filename: str | None = None):
        super().__init__("Compiler Token Error", details, line, col_st, col_end, filename)


class CompilerIfBlockError(Error):
    def __init__(self, details, line: int | None, col_st: int | None, col_end: int | None, filename: str | None = None):
        super().__init__("Compiler If-Block Error", details, line, col_st, col_end, filename)


class CompilerWhileBlockError(Error):
    def __init__(self, details, line: int | None, col_st: int | None, col_end: int | None, filename: str | None = None):
        super().__init__("Compiler While-Block Error", details, line, col_st, col_end, filename)
