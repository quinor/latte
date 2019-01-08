import typing
import enum
import attr
from . import ast, colors


class Kind(enum.Enum):
    pass


class ParseKind(Kind):
    NoDefaultValue = enum.auto()
    MalformedParenExpr = enum.auto()
    AmbiguousIf = enum.auto()
    ParserError = enum.auto()


class TypeAnalysisKind(Kind):
    VariableDoesNotExist = enum.auto()
    VariableRedeclaration = enum.auto()
    VariableShadow = enum.auto()
    MultipleFunctionDefinitions = enum.auto()
    NoMain = enum.auto()
    FunctionNotCallable = enum.auto()
    FunctionSameParameter = enum.auto()
    FunctionVoidParameter = enum.auto()
    FunctionDoesNotReturn = enum.auto()
    IncorrectArgumentCount = enum.auto()
    ArgumentTypeMismatch = enum.auto()
    AssignmentTypeMismatch = enum.auto()
    FunctionCallMismatch = enum.auto()
    ReturnTypeMismatch = enum.auto()
    ConditionTypeMismatch = enum.auto()
    DeadCode = enum.auto()


@attr.s(frozen=True, auto_attribs=True)
class Error:
    start: typing.Optional[ast.Position]
    end: typing.Optional[ast.Position]
    kind: Kind
    message: str


_l: typing.List[Error] = []


def clear_errors() -> None:
    _l.clear()


def errors() -> typing.List[Error]:
    return _l


def add_error(e: Error) -> None:
    _l.append(e)


def print_errors(code: str) -> None:
    lines = code.split("\n")
    for e in errors():
        print(
            f"at {e.start} to {e.end}\n{colors.red(e.kind.name)}:")
        print(f"    {e.message}")
        if e.start is None or e.end is None:
            continue

        st = max(e.start.line-3, 0)
        en = min(e.end.line+2, len(lines))
        for i in range(st, en):
            line = lines[i]
            print(f"{colors.white(str(i+1).rjust(4))}:   {colors.cyan(line)}")
            if i+1 == e.start.line and i+1 == e.end.line:
                print(" "*8+colors.red("".join(
                    "^" if e.start.column <= j and e.end.column >= j else " "
                    for j in range(len(line))
                )))
            elif i+1 == e.start.line:
                print(" "*8+colors.red(" "*e.start.column + "^"*(len(line) - e.start.column)))
            elif i+1 == e.end.line:
                print(" "*8+colors.red("^"*e.end.column + " "*(len(line) - e.end.column)))
            elif i+1 > e.start.line and i+1 < e.end.line:
                print(" "*8+colors.red("^"*len(line)))
        print()
