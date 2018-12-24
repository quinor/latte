import typing
import enum
import attr
from . import ast, colors


class Kind(enum.Enum):
    pass


class ParseKind(Kind):
    MalformedParenExpr = enum.auto()
    ParserError = enum.auto()


class AnalysisKind(Kind):
    VariableDoesNotExist = enum.auto()
    VariableShadow = enum.auto()
    FunctionNotCallable = enum.auto()
    FunctionSameParameter = enum.auto()
    FunctionDoesNotReturn = enum.auto()
    IncorrectArgumentCount = enum.auto()
    ArgumentTypeMismatch = enum.auto()
    AssignmentTypeMismatch = enum.auto()
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

def print_errors() -> None:
    for e in errors():
        print(
            f"at the {e.start} to the {e.end}\n{colors.red(e.kind.name)}:")
        print(f"    {e.message}")
        print()
